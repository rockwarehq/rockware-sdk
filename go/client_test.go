package rockware

// What the shared tests don't cover: inputs you don't set, hooks, token
// functions, calls by name, and ParseWebhook.

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"reflect"
	"testing"
	"time"
)

type roundTrip func(*http.Request) (*http.Response, error)

func (f roundTrip) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }

func answering(t *testing.T, bodies ...string) (*Client, *[][]byte) {
	t.Helper()
	sentBodies := &[][]byte{}
	client, err := NewClient(Config{
		Host:  "https://acme-api.example.com",
		Token: "rw_app_test",
		HTTPClient: &http.Client{Transport: roundTrip(func(r *http.Request) (*http.Response, error) {
			raw, _ := io.ReadAll(r.Body)
			*sentBodies = append(*sentBodies, raw)
			status, body := 200, bodies[len(*sentBodies)-1]
			if body == "" {
				status = 503
			}
			return &http.Response{StatusCode: status, Header: http.Header{}, Body: io.NopCloser(bytes.NewBufferString(body))}, nil
		})},
	})
	if err != nil {
		t.Fatal(err)
	}
	return client, sentBodies
}

func TestAnInputFieldYouDontSetIsntSent(t *testing.T) {
	client, sentBodies := answering(t, `{"data":{"upsertOrder":{"action":"UNCHANGED","order":null,"errors":[]}}}`)
	_, err := client.UpsertOrder(context.Background(), OrderInput{ExternalID: "SO-1", Notes: Ptr("rush")}, nil)
	if err != nil {
		t.Fatal(err)
	}
	var body struct {
		Variables map[string]map[string]any `json:"variables"`
	}
	_ = json.Unmarshal((*sentBodies)[0], &body)
	want := map[string]any{"externalId": "SO-1", "notes": "rush"}
	if !reflect.DeepEqual(body.Variables["order"], want) {
		t.Errorf("sent %v, want only %v", body.Variables["order"], want)
	}
	if _, ok := body.Variables["source"]; ok {
		t.Error("source was sent, but it wasn't set")
	}
}

func TestHooksAreCalledAndAPanicChangesNothing(t *testing.T) {
	var seen []string
	client, _ := answering(t, "", `{"data":{"site":{"id":"site_1"}}}`)
	client.hooks = Hooks{
		OnRequest: func(info RequestInfo) {
			seen = append(seen, info.Operation)
			panic("a broken hook")
		},
		OnRetry: func(info RequestInfo, err *Error, delay time.Duration) {
			seen = append(seen, string(err.Code))
		},
	}
	site, err := client.GetSite(context.Background())
	if err != nil || site == nil || site.ID != "site_1" {
		t.Fatalf("got %v, %v", site, err)
	}
	if want := []string{"GetSite", "api_error", "GetSite"}; !reflect.DeepEqual(seen, want) {
		t.Errorf("hooks saw %v, want %v", seen, want)
	}
}

func TestATokenFuncIsAskedOnEachCall(t *testing.T) {
	var tokens []string
	n := 0
	client, err := NewClient(Config{
		Host: "https://acme-api.example.com",
		TokenFunc: func(context.Context) (string, error) {
			n++
			return []string{"rw_app_1", "rw_app_2"}[n-1], nil
		},
		HTTPClient: &http.Client{Transport: roundTrip(func(r *http.Request) (*http.Response, error) {
			tokens = append(tokens, r.Header.Get("Authorization"))
			return &http.Response{StatusCode: 200, Header: http.Header{}, Body: io.NopCloser(bytes.NewBufferString(`{"data":{"site":{"id":"s"}}}`))}, nil
		})},
	})
	if err != nil {
		t.Fatal(err)
	}
	_, _ = client.GetSite(context.Background())
	_, _ = client.GetSite(context.Background())
	if want := []string{"Bearer rw_app_1", "Bearer rw_app_2"}; !reflect.DeepEqual(tokens, want) {
		t.Errorf("got %v", tokens)
	}
}

func TestAnyOperationCanBeSentByName(t *testing.T) {
	client, _ := answering(t, `{"data":{"site":{"id":"site_1"}}}`)
	raw, err := client.Call(context.Background(), "GetSite", nil)
	if err != nil || string(raw) != `{"id":"site_1"}` {
		t.Fatalf("got %s, %v", raw, err)
	}
	_, err = client.Call(context.Background(), "Nope", nil)
	var rwErr *Error
	if !errors.As(err, &rwErr) || rwErr.Code != CodeUsage {
		t.Errorf("got %v", err)
	}
}

func TestParseWebhook(t *testing.T) {
	body := []byte(`{"id":"evt_1","type":"order.updated","occurredAt":"2026-11-09T15:00:00.000Z","siteId":"site_1","data":{"object":"order","id":"ord_1"}}`)
	header := "t=1700000000,v1=236c14c5656906da5cdf38cecc494968b3b4c55aeef1d83818a866f6e046d75e"
	opts := &WebhookOptions{Now: time.Unix(1700000000, 0)}
	event, err := ParseWebhook("whsec_test", body, header, opts)
	if err != nil || event.ID != "evt_1" || event.Data.Object != "order" || event.Data.ID != "ord_1" {
		t.Fatalf("got %+v, %v", event, err)
	}
	_, err = ParseWebhook("whsec_other", body, header, opts)
	var rwErr *Error
	if !errors.As(err, &rwErr) || rwErr.Code != CodeForbidden {
		t.Errorf("got %v", err)
	}
}
