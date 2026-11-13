package rockware

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"strconv"
	"strings"
	"time"
)

// Webhook headers Rockware sends with each delivery.
const (
	SignatureHeader = "Rockware-Signature"
	EventIDHeader   = "Rockware-Event-Id"
	EventTypeHeader = "Rockware-Event-Type"
)

const defaultTolerance = 300 * time.Second

// WebhookOptions changes how a delivery is checked. Nil uses the defaults.
type WebhookOptions struct {
	// Tolerance is how far the signed time may be from now. 0 means 5 minutes.
	Tolerance time.Duration
	// Now is the time to check against. Zero means time.Now(). For tests.
	Now time.Time
}

// WebhookEvent is what Rockware sends: ids only. Fetch the record to see what changed.
type WebhookEvent struct {
	// ID is the event's id. Skip one you've already handled: the same event can arrive twice.
	ID string `json:"id"`
	// Type is like "order.updated".
	Type       string `json:"type"`
	OccurredAt string `json:"occurredAt"`
	SiteID     string `json:"siteId"`
	Data       struct {
		Object string `json:"object"`
		ID     string `json:"id"`
	} `json:"data"`
}

// VerifyWebhook reports whether the Rockware-Signature header signs this body,
// and its time is within the tolerance. Pass the raw body as it arrived.
func VerifyWebhook(secret string, body []byte, header string, opts *WebhookOptions) bool {
	if secret == "" || header == "" {
		return false
	}
	parts := map[string]string{}
	for _, part := range strings.Split(header, ",") {
		key, value, found := strings.Cut(part, "=")
		if found && strings.TrimSpace(key) != "" {
			parts[strings.TrimSpace(key)] = strings.TrimSpace(value)
		}
	}
	t, v1 := parts["t"], parts["v1"]
	if t == "" || strings.Trim(t, "0123456789") != "" || len(v1) != 64 {
		return false
	}
	given, err := hex.DecodeString(v1)
	if err != nil {
		return false
	}
	signed, err := strconv.ParseInt(t, 10, 64)
	if err != nil {
		return false
	}
	tolerance, now := defaultTolerance, time.Now()
	if opts != nil {
		if opts.Tolerance > 0 {
			tolerance = opts.Tolerance
		}
		if !opts.Now.IsZero() {
			now = opts.Now
		}
	}
	gap := now.Unix() - signed
	if gap < 0 {
		gap = -gap
	}
	if gap > int64(tolerance/time.Second) {
		return false
	}
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(t + "."))
	mac.Write(body)
	return hmac.Equal(mac.Sum(nil), given)
}

// ParseWebhook checks the signature, then reads the event. A wrong or old
// signature is an *Error with CodeForbidden.
func ParseWebhook(secret string, body []byte, header string, opts *WebhookOptions) (WebhookEvent, error) {
	var event WebhookEvent
	if !VerifyWebhook(secret, body, header, opts) {
		return event, newError(CodeForbidden, "The webhook's signature is wrong or too old")
	}
	if err := json.Unmarshal(body, &event); err != nil {
		e := newError(CodeValidation, "The webhook's body isn't JSON")
		e.cause = err
		return event, e
	}
	return event, nil
}
