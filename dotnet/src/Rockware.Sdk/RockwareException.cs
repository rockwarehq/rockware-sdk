using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Rockware;

/// <summary>How a call failed. See SPEC.md, Errors.</summary>
public enum ErrorCode
{
    /// <summary>A bad setting or argument, found before sending.</summary>
    Usage,

    /// <summary>The token is wrong, revoked or for another plant.</summary>
    AuthRequired,

    /// <summary>The token is missing a scope.</summary>
    Forbidden,

    /// <summary>The thing named isn't there.</summary>
    NotFound,

    /// <summary>The request isn't right: a bad argument, or too big a query.</summary>
    Validation,

    /// <summary>Too many requests. RetryAfter says how long to wait.</summary>
    RateLimit,

    /// <summary>The server failed, or sent something the SDK can't read.</summary>
    ApiError,

    /// <summary>No answer from the host.</summary>
    Network,
}

/// <summary>One error as the server sent it.</summary>
public sealed class GraphQLError
{
    /// <summary>What went wrong.</summary>
    [JsonPropertyName("message")]
    public string Message { get; set; } = "";

    /// <summary>Where in the answer, if the server said.</summary>
    [JsonPropertyName("path")]
    public List<JsonElement>? Path { get; set; }

    /// <summary>More about it, like its code.</summary>
    [JsonPropertyName("extensions")]
    public Dictionary<string, JsonElement>? Extensions { get; set; }
}

/// <summary>Every way a call to Rockware can fail. <see cref="Code"/> says how.</summary>
public sealed class RockwareException : Exception
{
    private const int MaxMessageLength = 500;

    /// <summary>Makes one. The SDK makes these; you don't need to.</summary>
    public RockwareException(ErrorCode code, string message, Exception? inner = null)
        : base(Truncate(message), inner)
    {
        Code = code;
    }

    /// <summary>How it failed.</summary>
    public ErrorCode Code { get; }

    /// <summary>What to do about it, when the SDK knows.</summary>
    public string? Hint { get; init; }

    /// <summary>The HTTP status, when there was an answer.</summary>
    public int? HttpStatus { get; init; }

    /// <summary>Whether trying again later might work.</summary>
    public bool Retryable { get; init; }

    /// <summary>How long the server asked to wait.</summary>
    public TimeSpan? RetryAfter { get; init; }

    /// <summary>The server's id for the request. Give it to Rockware support.</summary>
    public string? RequestId { get; init; }

    /// <summary>The server's own code (extensions.code), as sent.</summary>
    public string? ServerCode { get; init; }

    /// <summary>Every GraphQL error the server sent, as sent.</summary>
    public IReadOnlyList<GraphQLError> Errors { get; init; } = Array.Empty<GraphQLError>();

    private static string Truncate(string message) =>
        message.Length > MaxMessageLength ? message.Substring(0, MaxMessageLength - 1) + "…" : message;

    internal static ErrorCode CodeForStatus(int status) =>
        status switch
        {
            400 => ErrorCode.Validation,
            401 => ErrorCode.AuthRequired,
            403 => ErrorCode.Forbidden,
            404 => ErrorCode.NotFound,
            429 => ErrorCode.RateLimit,
            _ => ErrorCode.ApiError,
        };

    internal static ErrorCode CodeForServerCode(string? serverCode) =>
        serverCode switch
        {
            "UNAUTHENTICATED" => ErrorCode.AuthRequired,
            "FORBIDDEN" => ErrorCode.Forbidden,
            "NOT_FOUND" => ErrorCode.NotFound,
            "BAD_USER_INPUT" or "GRAPHQL_VALIDATION_FAILED" or "GRAPHQL_PARSE_FAILED" => ErrorCode.Validation,
            _ => ErrorCode.ApiError,
        };

    internal static string? HintFor(ErrorCode code, TimeSpan? retryAfter) =>
        code switch
        {
            ErrorCode.AuthRequired => "Check the token. It may be mistyped, revoked, or for a different plant.",
            ErrorCode.Forbidden =>
                "The token may be missing a scope. A plant admin can make one with it under Settings → Developers.",
            ErrorCode.RateLimit => retryAfter is { } wait
                ? $"Wait {(int)wait.TotalSeconds} seconds, then try again."
                : "Wait a minute, then try again.",
            ErrorCode.Network => "Check the host, and that this machine can reach it.",
            _ => null,
        };
}
