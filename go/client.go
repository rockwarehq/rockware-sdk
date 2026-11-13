// Package rockware calls Rockware's developer API: read and send a plant's
// records, page through them, and check webhook deliveries.
//
//	client, err := rockware.NewClient(rockware.Config{
//		Host:  "https://acme-api.rockware.io",
//		Token: os.Getenv("ROCKWARE_TOKEN"),
//	})
//	for product, err := range client.ListAllProducts(ctx, nil) {
//		if err != nil {
//			return err
//		}
//		fmt.Println(product.Sku)
//	}
//
// How every Rockware SDK behaves is in SPEC.md at the repo's root.
package rockware

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"iter"
	"math"
	"math/rand/v2"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

const (
	defaultTimeout  = 30 * time.Second
	defaultMaxPages = 10_000
	sdkAgent        = "rockware-sdk-go/" + Version
)

// Config is how to make a Client. Host and either Token or TokenFunc are required.
type Config struct {
	// Host is the plant's API host, like https://acme-api.rockware.io.
	Host string
	// Token is an API token (rw_app_…) or a connected token (rw_mcp_…).
	Token string
	// TokenFunc gives a token for each call, instead of Token.
	TokenFunc func(ctx context.Context) (string, error)
	// Timeout is for each attempt. 0 means 30 seconds.
	Timeout time.Duration
	// NoRetry turns retries off.
	NoRetry bool
	// UserAgent is your app's name and version, like acme-erp-sync/2.1.
	UserAgent string
	Hooks     Hooks
	// HTTPClient sends the requests, for proxies or tests. Nil means a new one.
	HTTPClient *http.Client
}

// RequestInfo describes one attempt, for hooks.
type RequestInfo struct {
	Operation string
	// Attempt is 1 for the first try.
	Attempt int
	URL     string
}

// ResponseInfo describes how one attempt went, for hooks.
type ResponseInfo struct {
	// HTTPStatus is 0 when there was no answer.
	HTTPStatus int
	Duration   time.Duration
	Err        *Error
}

// Hooks let you watch a client work. Each is optional. A panic in one is recovered and ignored.
type Hooks struct {
	OnRequest  func(RequestInfo)
	OnResponse func(RequestInfo, ResponseInfo)
	OnRetry    func(info RequestInfo, err *Error, delay time.Duration)
}

// Client is Rockware's developer API. It's safe to use from many goroutines.
type Client struct {
	host      string
	token     func(ctx context.Context) (string, error)
	timeout   time.Duration
	retry     bool
	userAgent string
	hooks     Hooks
	http      *http.Client
}

// NewClient checks the config and makes a client. A bad setting is an *Error with CodeUsage.
func NewClient(config Config) (*Client, error) {
	host, err := checkHost(config.Host)
	if err != nil {
		return nil, err
	}
	token := config.TokenFunc
	if token == nil {
		if strings.TrimSpace(config.Token) == "" {
			return nil, newError(CodeUsage, "A token is required")
		}
		fixed := config.Token
		token = func(context.Context) (string, error) { return fixed, nil }
	}
	timeout := config.Timeout
	if timeout == 0 {
		timeout = defaultTimeout
	}
	if timeout < 0 {
		return nil, newError(CodeUsage, "Timeout must be more than 0")
	}
	userAgent := sdkAgent
	if agent := strings.TrimSpace(config.UserAgent); agent != "" {
		userAgent = agent + " " + sdkAgent
	}
	// Redirects are never followed (SPEC.md, Security), even with your own
	// HTTPClient: the client uses a copy of it that stops at a redirect.
	httpClient := &http.Client{}
	if config.HTTPClient != nil {
		copied := *config.HTTPClient
		httpClient = &copied
	}
	httpClient.CheckRedirect = func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }
	return &Client{
		host:      host,
		token:     token,
		timeout:   timeout,
		retry:     !config.NoRetry,
		userAgent: userAgent,
		hooks:     config.Hooks,
		http:      httpClient,
	}, nil
}

// Host is the host the client sends to.
func (c *Client) Host() string { return c.host }

// Call sends any operation from operations/ by name, and gives back its root
// field as raw JSON. The methods are easier; this is for tools.
func (c *Client) Call(ctx context.Context, name string, variables map[string]any) (json.RawMessage, error) {
	op, ok := operations[name]
	if !ok {
		return nil, newError(CodeUsage, "No operation named "+name)
	}
	var out json.RawMessage
	if err := c.run(ctx, op, variables, &out); err != nil {
		return nil, err
	}
	return out, nil
}

// Ptr gives a pointer to v, for optional arguments: &ListProductsOptions{First: rockware.Ptr(50)}.
func Ptr[T any](v T) *T { return &v }

type operation struct {
	name         string
	root         string
	mutation     bool
	safeToRepeat bool
	document     string
}

func (c *Client) run(ctx context.Context, op *operation, variables map[string]any, out any) error {
	token, err := c.token(ctx)
	if err != nil {
		return err
	}
	if strings.TrimSpace(token) == "" {
		return newError(CodeUsage, "A token is required")
	}
	body, err := json.Marshal(map[string]any{"query": op.document, "variables": variables, "operationName": op.name})
	if err != nil {
		e := newError(CodeUsage, "Can't send these arguments: "+err.Error())
		e.cause = err
		return e
	}
	endpoint := c.host + "/graphql"
	attempts := 1
	if c.retry {
		attempts = retryAttempts
	}
	for attempt := 1; ; attempt++ {
		info := RequestInfo{Operation: op.name, Attempt: attempt, URL: endpoint}
		safely(func() {
			if c.hooks.OnRequest != nil {
				c.hooks.OnRequest(info)
			}
		})
		started := time.Now()
		status, data, failure := c.send(ctx, endpoint, token, body)
		if ctx.Err() != nil {
			return ctx.Err()
		}
		if failure != nil {
			failure = redact(failure, token)
		}
		safely(func() {
			if c.hooks.OnResponse != nil {
				c.hooks.OnResponse(info, ResponseInfo{HTTPStatus: status, Duration: time.Since(started), Err: failure})
			}
		})
		if failure == nil {
			root, ok := data[op.root]
			if !ok {
				return newError(CodeAPIError, "The server's answer has no "+op.root)
			}
			if err := json.Unmarshal(root, out); err != nil {
				e := newError(CodeAPIError, "Can't read the server's answer: "+err.Error())
				e.cause = err
				return e
			}
			return nil
		}
		delay, again := retryDelay(failure, op, attempt)
		if !again || attempt >= attempts {
			return failure
		}
		safely(func() {
			if c.hooks.OnRetry != nil {
				c.hooks.OnRetry(info, failure, delay)
			}
		})
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(delay):
		}
	}
}

// send makes one attempt. It gives the status, the data, or the error the answer means.
func (c *Client) send(ctx context.Context, endpoint, token string, body []byte) (int, map[string]json.RawMessage, *Error) {
	attemptCtx, cancel := context.WithTimeout(ctx, c.timeout)
	defer cancel()
	request, err := http.NewRequestWithContext(attemptCtx, http.MethodPost, endpoint, bytes.NewReader(body))
	if err != nil {
		return 0, nil, newError(CodeUsage, err.Error())
	}
	request.Header.Set("Authorization", "Bearer "+token)
	request.Header.Set("Content-Type", "application/json")
	request.Header.Set("Accept", "application/json")
	request.Header.Set("User-Agent", c.userAgent)

	response, err := c.http.Do(request)
	if err != nil {
		var e *Error
		if errors.Is(attemptCtx.Err(), context.DeadlineExceeded) && ctx.Err() == nil {
			e = newError(CodeNetwork, fmt.Sprintf("%s didn't answer within %s", c.host, c.timeout))
		} else {
			e = newError(CodeNetwork, fmt.Sprintf("Can't reach %s: %v", c.host, err))
		}
		e.Retryable, e.Hint, e.cause = true, hintFor(CodeNetwork, 0), err
		return 0, nil, e
	}
	defer response.Body.Close()
	text, _ := io.ReadAll(response.Body)
	data, failure := readAnswer(response, text)
	return response.StatusCode, data, failure
}

func readAnswer(response *http.Response, text []byte) (map[string]json.RawMessage, *Error) {
	status := response.StatusCode
	var body struct {
		Data   json.RawMessage `json:"data"`
		Errors []GraphQLError  `json:"errors"`
	}
	parsed := len(text) > 0 && json.Unmarshal(text, &body) == nil
	serverCode := ""
	if len(body.Errors) > 0 {
		if code, ok := body.Errors[0].Extensions["code"].(string); ok {
			serverCode = code
		}
	}
	messages := make([]string, 0, len(body.Errors))
	for _, e := range body.Errors {
		messages = append(messages, e.Message)
	}
	retryAfter := parseRetryAfter(response.Header.Get("Retry-After"))
	fill := func(e *Error) *Error {
		e.HTTPStatus, e.RequestID, e.RetryAfter = status, response.Header.Get("X-Request-Id"), retryAfter
		e.ServerCode, e.Errors = serverCode, body.Errors
		return e
	}

	if status < 200 || status >= 300 {
		code := codeForStatus(status)
		message := strings.Join(messages, "; ")
		if message == "" {
			message = fmt.Sprintf("The server answered HTTP %d", status)
		}
		e := fill(newError(code, message))
		e.Retryable = code == CodeRateLimit || status >= 500
		e.Hint = hintFor(code, retryAfter)
		return nil, e
	}
	if !parsed {
		return nil, fill(newError(CodeAPIError, fmt.Sprintf("The server's answer isn't JSON (HTTP %d)", status)))
	}
	if len(body.Errors) > 0 {
		code := codeForServerCode(serverCode)
		e := fill(newError(code, strings.Join(messages, "; ")))
		e.Hint = hintFor(code, 0)
		return nil, e
	}
	var data map[string]json.RawMessage
	if len(body.Data) == 0 || json.Unmarshal(body.Data, &data) != nil || data == nil {
		return nil, fill(newError(CodeAPIError, "The server's answer has no data"))
	}
	return data, nil
}

// parseRetryAfter reads whole seconds, or an HTTP date still ahead. 0 means none.
func parseRetryAfter(value string) time.Duration {
	value = strings.TrimSpace(value)
	if value == "" {
		return 0
	}
	if seconds, err := strconv.Atoi(value); err == nil && seconds >= 0 {
		return time.Duration(seconds) * time.Second
	}
	date, err := http.ParseTime(value)
	if err != nil {
		return 0
	}
	ahead := time.Until(date)
	if ahead <= 0 {
		return 0
	}
	return time.Duration(math.Ceil(ahead.Seconds())) * time.Second
}

// retryDelay says how long to wait before trying again, and whether to. SPEC.md section 5.
func retryDelay(e *Error, op *operation, attempt int) (time.Duration, bool) {
	refusedBeforeRunning := e.Code == CodeRateLimit
	mightHaveRun := e.Code == CodeNetwork || e.HTTPStatus >= 500
	if !refusedBeforeRunning && !(mightHaveRun && op.safeToRepeat) {
		return 0, false
	}
	if e.RetryAfter > 0 {
		return e.RetryAfter, e.RetryAfter <= maxRetryAfter
	}
	jitter := time.Duration(rand.Int64N(int64(retryMaxJitter)))
	return retryBaseDelay*time.Duration(1<<(attempt-1)) + jitter, true
}

// redact keeps the token out of an error.
func redact(e *Error, token string) *Error {
	if !strings.Contains(e.Message, token) {
		return e
	}
	copied := *e
	copied.Message = strings.ReplaceAll(e.Message, token, "[hidden]")
	copied.Errors = make([]GraphQLError, len(e.Errors))
	for i, ge := range e.Errors {
		ge.Message = strings.ReplaceAll(ge.Message, token, "[hidden]")
		copied.Errors[i] = ge
	}
	return &copied
}

func checkHost(host string) (string, error) {
	parsed, err := url.Parse(host)
	if err != nil || parsed.Scheme == "" || parsed.Hostname() == "" {
		return "", newError(CodeUsage, "Host isn't a URL: "+host)
	}
	local := parsed.Hostname() == "localhost" || parsed.Hostname() == "127.0.0.1" || parsed.Hostname() == "::1"
	if parsed.Scheme != "https" && !(parsed.Scheme == "http" && local) {
		return "", newError(CodeUsage, "Host must use https://, except localhost")
	}
	return strings.TrimRight(host, "/"), nil
}

type page[N any] struct {
	Nodes    []N `json:"nodes"`
	PageInfo struct {
		HasNextPage bool    `json:"hasNextPage"`
		EndCursor   *string `json:"endCursor"`
	} `json:"pageInfo"`
}

func listAll[N any](ctx context.Context, c *Client, op *operation, vars map[string]any, maxPages int) iter.Seq2[N, error] {
	if maxPages == 0 {
		maxPages = defaultMaxPages
	}
	return func(yield func(N, error) bool) {
		var zero N
		if maxPages < 0 {
			yield(zero, newError(CodeUsage, "MaxPages must be more than 0"))
			return
		}
		args := make(map[string]any, len(vars)+1)
		for k, v := range vars {
			args[k] = v
		}
		for n := 1; ; n++ {
			var got page[N]
			if err := c.run(ctx, op, args, &got); err != nil {
				yield(zero, err)
				return
			}
			for _, node := range got.Nodes {
				if !yield(node, nil) {
					return
				}
			}
			if !got.PageInfo.HasNextPage || got.PageInfo.EndCursor == nil || *got.PageInfo.EndCursor == "" || n >= maxPages {
				return
			}
			args["after"] = *got.PageInfo.EndCursor
		}
	}
}

func safely(hook func()) {
	defer func() { _ = recover() }()
	hook()
}
