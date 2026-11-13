package rockware

import (
	"fmt"
	"time"
	"unicode/utf8"
)

// ErrorCode says how a call failed. See SPEC.md, Errors.
type ErrorCode string

const (
	// CodeUsage is a bad setting or argument, found before sending.
	CodeUsage ErrorCode = "usage"
	// CodeAuthRequired means the token is wrong, revoked or for another plant.
	CodeAuthRequired ErrorCode = "auth_required"
	// CodeForbidden means the token is missing a scope.
	CodeForbidden ErrorCode = "forbidden"
	// CodeNotFound means the thing named isn't there.
	CodeNotFound ErrorCode = "not_found"
	// CodeValidation means the request isn't right: a bad argument, or too big a query.
	CodeValidation ErrorCode = "validation"
	// CodeRateLimit means too many requests. RetryAfter says how long to wait.
	CodeRateLimit ErrorCode = "rate_limit"
	// CodeAPIError means the server failed, or sent something the SDK can't read.
	CodeAPIError ErrorCode = "api_error"
	// CodeNetwork means there was no answer from the host.
	CodeNetwork ErrorCode = "network"
)

const maxMessageLength = 500

// GraphQLError is one error as the server sent it.
type GraphQLError struct {
	Message    string         `json:"message"`
	Path       []any          `json:"path,omitempty"`
	Extensions map[string]any `json:"extensions,omitempty"`
}

// Error is every way a call can fail. Use errors.As to get one.
type Error struct {
	Code    ErrorCode
	Message string
	// Hint says what to do about it, when the SDK knows.
	Hint string
	// HTTPStatus is the HTTP status, or 0 when there was no answer.
	HTTPStatus int
	// Retryable says whether trying again later might work.
	Retryable bool
	// RetryAfter is how long the server asked to wait, or 0 if it didn't say.
	RetryAfter time.Duration
	// RequestID is the server's id for the request. Give it to Rockware support.
	RequestID string
	// ServerCode is the server's own code (extensions.code), as sent.
	ServerCode string
	// Errors is every GraphQL error the server sent, as sent.
	Errors []GraphQLError

	cause error
}

func (e *Error) Error() string {
	return fmt.Sprintf("rockware: %s: %s", e.Code, e.Message)
}

// Unwrap gives the error underneath, like a network error.
func (e *Error) Unwrap() error { return e.cause }

func newError(code ErrorCode, message string) *Error {
	if utf8.RuneCountInString(message) > maxMessageLength {
		runes := []rune(message)
		message = string(runes[:maxMessageLength-1]) + "…"
	}
	return &Error{Code: code, Message: message}
}

var serverCodes = map[string]ErrorCode{
	"UNAUTHENTICATED":           CodeAuthRequired,
	"FORBIDDEN":                 CodeForbidden,
	"NOT_FOUND":                 CodeNotFound,
	"BAD_USER_INPUT":            CodeValidation,
	"GRAPHQL_VALIDATION_FAILED": CodeValidation,
	"GRAPHQL_PARSE_FAILED":      CodeValidation,
}

func codeForStatus(status int) ErrorCode {
	switch status {
	case 400:
		return CodeValidation
	case 401:
		return CodeAuthRequired
	case 403:
		return CodeForbidden
	case 404:
		return CodeNotFound
	case 429:
		return CodeRateLimit
	}
	return CodeAPIError
}

func codeForServerCode(serverCode string) ErrorCode {
	if code, ok := serverCodes[serverCode]; ok {
		return code
	}
	return CodeAPIError
}

func hintFor(code ErrorCode, retryAfter time.Duration) string {
	switch code {
	case CodeAuthRequired:
		return "Check the token. It may be mistyped, revoked, or for a different plant."
	case CodeForbidden:
		return "The token may be missing a scope. A plant admin can make one with it under Settings → Developers."
	case CodeRateLimit:
		if retryAfter > 0 {
			return fmt.Sprintf("Wait %d seconds, then try again.", int(retryAfter.Seconds()))
		}
		return "Wait a minute, then try again."
	case CodeNetwork:
		return "Check the host, and that this machine can reach it."
	}
	return ""
}
