package rockware

// Runs the repo's shared tests (conformance/) against this SDK. A fake HTTP
// transport plays the server. See conformance/README.md for the format.

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math"
	"net/http"
	"os"
	"path/filepath"
	"reflect"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"testing"
	"time"
)

type answer struct {
	Status       int               `json:"status"`
	Headers      map[string]string `json:"headers"`
	Body         json.RawMessage   `json:"body"`
	RawBody      *string           `json:"rawBody"`
	NetworkError bool              `json:"networkError"`
}

type conformanceCase struct {
	Name   string `json:"name"`
	Client struct {
		Host      *string `json:"host"`
		Token     *string `json:"token"`
		UserAgent string  `json:"userAgent"`
		Retry     *bool   `json:"retry"`
	} `json:"client"`
	Operation  string                     `json:"operation"`
	Variables  map[string]json.RawMessage `json:"variables"`
	Paginate   bool                       `json:"paginate"`
	MaxPages   int                        `json:"maxPages"`
	Responses  []answer                   `json:"responses"`
	Assertions []map[string]any           `json:"assertions"`
}

type sent struct {
	at      time.Time
	method  string
	url     string
	headers http.Header
	body    any
}

type fakeServer struct {
	mu      sync.Mutex
	answers []answer
	sent    []sent
}

var httpDate = regexp.MustCompile(`\{\{httpdate\+(\d{1,9})s\}\}`)

func (f *fakeServer) RoundTrip(request *http.Request) (*http.Response, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	raw, _ := io.ReadAll(request.Body)
	var body any
	_ = json.Unmarshal(raw, &body)
	f.sent = append(f.sent, sent{time.Now(), request.Method, request.URL.String(), request.Header.Clone(), body})
	if len(f.sent) > len(f.answers) {
		return nil, fmt.Errorf("the test has no answer for request %d", len(f.sent))
	}
	a := f.answers[len(f.sent)-1]
	if a.NetworkError {
		return nil, errors.New("connection dropped")
	}
	headers := http.Header{}
	for name, value := range a.Headers {
		headers.Set(name, httpDate.ReplaceAllStringFunc(value, func(token string) string {
			seconds, _ := strconv.Atoi(httpDate.FindStringSubmatch(token)[1])
			return time.Unix(time.Now().Unix()+int64(seconds)+1, 0).UTC().Format(http.TimeFormat)
		}))
	}
	content := []byte{}
	if a.RawBody != nil {
		content = []byte(*a.RawBody)
	} else if len(a.Body) > 0 {
		content = a.Body
	}
	status := a.Status
	if status == 0 {
		status = 200
	}
	return &http.Response{
		StatusCode: status,
		Header:     headers,
		Body:       io.NopCloser(bytes.NewReader(content)),
		Request:    request,
	}, nil
}

func at(value any, path string) (any, bool) {
	if path == "" {
		return value, true
	}
	current := value
	for _, key := range strings.Split(path, ".") {
		switch typed := current.(type) {
		case []any:
			if key == "length" {
				current = float64(len(typed))
				continue
			}
			i, err := strconv.Atoi(key)
			if err != nil || i >= len(typed) {
				return nil, false
			}
			current = typed[i]
		case map[string]any:
			next, ok := typed[key]
			if !ok {
				return nil, false
			}
			current = next
		default:
			return nil, false
		}
	}
	return current, true
}

// asJSON turns a result into plain JSON values, the same shape the server sent.
func asJSON(value any) any {
	raw, _ := json.Marshal(value)
	var out any
	_ = json.Unmarshal(raw, &out)
	return out
}

func same(a, b any) bool { return reflect.DeepEqual(asJSON(a), asJSON(b)) }

func run(t *testing.T, test conformanceCase) (*fakeServer, any, error) {
	server := &fakeServer{answers: test.Responses}
	config := Config{Host: "https://acme-api.example.com", Token: "rw_app_test", UserAgent: test.Client.UserAgent}
	if test.Client.Host != nil {
		config.Host = *test.Client.Host
	}
	if test.Client.Token != nil {
		config.Token = *test.Client.Token
	}
	if test.Client.Retry != nil {
		config.NoRetry = !*test.Client.Retry
	}
	config.HTTPClient = &http.Client{Transport: server}
	client, err := NewClient(config)
	if err != nil {
		return server, nil, err
	}
	vars := test.Variables
	if vars == nil {
		vars = map[string]json.RawMessage{}
	}
	if test.Paginate {
		collected := []any{}
		each := func(record any) { collected = append(collected, record) }
		err := pages[test.Operation](context.Background(), client, vars, test.MaxPages, each)
		return server, collected, err
	}
	call, ok := calls[test.Operation]
	if !ok {
		t.Fatalf("no operation %s", test.Operation)
	}
	result, err := call(context.Background(), client, vars)
	return server, result, err
}

func TestConformance(t *testing.T) {
	files, _ := filepath.Glob(filepath.Join("..", "conformance", "tests", "*.json"))
	if len(files) == 0 {
		t.Fatal("no conformance tests found")
	}
	for _, file := range files {
		raw, err := os.ReadFile(file)
		if err != nil {
			t.Fatal(err)
		}
		var cases []conformanceCase
		if err := json.Unmarshal(raw, &cases); err != nil {
			t.Fatalf("%s: %v", file, err)
		}
		for _, test := range cases {
			t.Run(strings.TrimSuffix(filepath.Base(file), ".json")+"/"+test.Name, func(t *testing.T) {
				t.Parallel()
				check(t, test)
			})
		}
	}
}

func check(t *testing.T, test conformanceCase) {
	server, result, err := run(t, test)
	var rwErr *Error
	isRwErr := errors.As(err, &rwErr)
	for _, a := range test.Assertions {
		index := 0
		if i, ok := a["index"].(float64); ok {
			index = int(i)
		}
		kind, _ := a["type"].(string)
		request := func() sent {
			if index >= len(server.sent) {
				t.Fatalf("%s: no request %d", kind, index)
			}
			return server.sent[index]
		}
		switch kind {
		case "requestCount":
			if got := len(server.sent); float64(got) != a["expected"] {
				t.Errorf("requests: got %d, want %v", got, a["expected"])
			}
		case "requestMethod":
			if got := request().method; got != a["expected"] {
				t.Errorf("method: got %s", got)
			}
		case "requestUrl":
			if got := request().url; got != a["expected"] {
				t.Errorf("url: got %s", got)
			}
		case "requestHeader":
			got := request().headers.Get(a["name"].(string))
			if want, ok := a["expected"]; ok && got != want {
				t.Errorf("header %s: got %q, want %q", a["name"], got, want)
			}
			if pattern, ok := a["pattern"].(string); ok && !regexp.MustCompile(pattern).MatchString(got) {
				t.Errorf("header %s: %q doesn't match %s", a["name"], got, pattern)
			}
		case "requestBody":
			path := a["path"].(string)
			got, found := at(request().body, path)
			if absent, _ := a["absent"].(bool); absent && found {
				t.Errorf("%s: want it left out, got %v", path, got)
			}
			if want, ok := a["expected"]; ok && !same(got, want) {
				t.Errorf("%s: got %v, want %v", path, got, want)
			}
			if pattern, ok := a["pattern"].(string); ok && !regexp.MustCompile(pattern).MatchString(fmt.Sprint(got)) {
				t.Errorf("%s doesn't match %s", path, pattern)
			}
			if want, ok := a["expectedInstant"].(string); ok {
				gotTime, err1 := time.Parse(time.RFC3339Nano, fmt.Sprint(got))
				wantTime, err2 := time.Parse(time.RFC3339Nano, want)
				if err1 != nil || err2 != nil || !gotTime.Equal(wantTime) {
					t.Errorf("%s: got %v, want the moment %s", path, got, want)
				}
			}
		case "delayBetweenRequests":
			if index+1 >= len(server.sent) {
				t.Fatalf("no request after %d", index)
			}
			gap := float64(server.sent[index+1].at.Sub(server.sent[index].at).Milliseconds())
			if gap < a["minMs"].(float64) {
				t.Errorf("gap after request %d: %vms, want at least %v", index, gap, a["minMs"])
			}
			if most, ok := a["maxMs"].(float64); ok && gap > most {
				t.Errorf("gap after request %d: %vms, want at most %v", index, gap, most)
			}
		case "noError":
			if err != nil {
				t.Errorf("want no error, got %v", err)
			}
		case "error":
			if !isRwErr {
				t.Fatalf("want a *rockware.Error, got %v", err)
			}
			fields := map[string]any{
				"code":       string(rwErr.Code),
				"httpStatus": float64(rwErr.HTTPStatus),
				"retryable":  rwErr.Retryable,
				"retryAfter": math.Round(rwErr.RetryAfter.Seconds()),
				"requestId":  rwErr.RequestID,
				"serverCode": rwErr.ServerCode,
			}
			for name, got := range fields {
				if want, ok := a[name]; ok && !same(got, want) {
					t.Errorf("error %s: got %v, want %v", name, got, want)
				}
			}
		case "errorMessage":
			if !isRwErr {
				t.Fatalf("want a *rockware.Error, got %v", err)
			}
			if pattern, ok := a["pattern"].(string); ok && !regexp.MustCompile(pattern).MatchString(rwErr.Message) {
				t.Errorf("message %q doesn't match %s", rwErr.Message, pattern)
			}
			if excludes, ok := a["excludes"].(string); ok && strings.Contains(rwErr.Message, excludes) {
				t.Errorf("message %q has %q", rwErr.Message, excludes)
			}
		case "errorMessageLength":
			if !isRwErr || float64(len([]rune(rwErr.Message))) > a["max"].(float64) {
				t.Errorf("message too long: %d", len([]rune(rwErr.Message)))
			}
		case "errorCount":
			if !isRwErr || float64(len(rwErr.Errors)) != a["expected"] {
				t.Errorf("errors: got %v", err)
			}
		case "result":
			path := a["path"].(string)
			got, _ := at(asJSON(result), path)
			if !same(got, a["expected"]) {
				t.Errorf("result %q: got %v, want %v", path, got, a["expected"])
			}
		default:
			t.Fatalf("unknown assertion type %s", kind)
		}
	}
}

func TestWebhookSignatures(t *testing.T) {
	raw, err := os.ReadFile(filepath.Join("..", "conformance", "webhooks.json"))
	if err != nil {
		t.Fatal(err)
	}
	var file struct {
		Cases []struct {
			Name      string `json:"name"`
			Secret    string `json:"secret"`
			Body      string `json:"body"`
			Header    string `json:"header"`
			Now       int64  `json:"now"`
			Tolerance int    `json:"tolerance"`
			Valid     bool   `json:"valid"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(raw, &file); err != nil {
		t.Fatal(err)
	}
	for _, c := range file.Cases {
		t.Run(c.Name, func(t *testing.T) {
			opts := &WebhookOptions{Now: time.Unix(c.Now, 0), Tolerance: time.Duration(c.Tolerance) * time.Second}
			if got := VerifyWebhook(c.Secret, []byte(c.Body), c.Header, opts); got != c.Valid {
				t.Errorf("got %v, want %v", got, c.Valid)
			}
		})
	}
}
