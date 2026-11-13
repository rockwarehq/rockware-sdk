using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace Rockware;

/// <summary>How to make a <see cref="RockwareClient"/>. Host and a token are required.</summary>
public sealed class RockwareOptions
{
    /// <summary>The plant's API host, like https://acme-api.rockware.io.</summary>
    public string Host { get; set; } = "";

    /// <summary>An API token (rw_app_…) or a connected token (rw_mcp_…).</summary>
    public string? Token { get; set; }

    /// <summary>Gives a token for each call, instead of <see cref="Token"/>.</summary>
    public Func<CancellationToken, ValueTask<string>>? TokenProvider { get; set; }

    /// <summary>For each attempt. Default 30 seconds.</summary>
    public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);

    /// <summary>Retry when it's safe. Default true.</summary>
    public bool Retry { get; set; } = true;

    /// <summary>Your app's name and version, like acme-erp-sync/2.1.</summary>
    public string? UserAgent { get; set; }

    /// <summary>Ways to watch the client work.</summary>
    public RockwareHooks? Hooks { get; set; }

    /// <summary>
    /// Sends the requests, for proxies or tests. The client never follows
    /// redirects; an HttpClientHandler given here has redirects turned off.
    /// </summary>
    public HttpMessageHandler? HttpHandler { get; set; }
}

/// <summary>One attempt, for hooks.</summary>
public sealed class RequestInfo
{
    internal RequestInfo(string operation, int attempt, string url)
    {
        Operation = operation;
        Attempt = attempt;
        Url = url;
    }

    /// <summary>The operation's name.</summary>
    public string Operation { get; }

    /// <summary>1 for the first try.</summary>
    public int Attempt { get; }

    /// <summary>Where it went.</summary>
    public string Url { get; }
}

/// <summary>How one attempt went, for hooks.</summary>
public sealed class ResponseInfo
{
    internal ResponseInfo(int? httpStatus, TimeSpan duration, RockwareException? error)
    {
        HttpStatus = httpStatus;
        Duration = duration;
        Error = error;
    }

    /// <summary>The HTTP status, or null when there was no answer.</summary>
    public int? HttpStatus { get; }

    /// <summary>How long it took.</summary>
    public TimeSpan Duration { get; }

    /// <summary>What went wrong, if anything.</summary>
    public RockwareException? Error { get; }
}

/// <summary>Ways to watch a client work. Each is optional. An exception thrown in one is ignored.</summary>
public sealed class RockwareHooks
{
    /// <summary>Before each attempt.</summary>
    public Action<RequestInfo>? OnRequest { get; set; }

    /// <summary>After each attempt.</summary>
    public Action<RequestInfo, ResponseInfo>? OnResponse { get; set; }

    /// <summary>Before waiting to try again.</summary>
    public Action<RequestInfo, RockwareException, TimeSpan>? OnRetry { get; set; }
}

/// <summary>
/// Rockware's developer API. Make one and keep it: it's safe to use from many threads.
/// <code>
/// using var rockware = new RockwareClient(new RockwareOptions { Host = "https://acme-api.rockware.io", Token = token });
/// await foreach (var product in rockware.ListAllProductsAsync()) Console.WriteLine(product.Sku);
/// </code>
/// </summary>
public sealed partial class RockwareClient : IDisposable
{
    /// <summary>The page limit for ListAll… methods.</summary>
    public const int DefaultMaxPages = 10_000;

    /// <summary>This SDK's version.</summary>
    public const string Version = Behavior.Version;

    private const string SdkAgent = "rockware-sdk-dotnet/" + Behavior.Version;

    /// <summary>How the SDK reads and writes JSON.</summary>
    public static readonly JsonSerializerOptions JsonOptions = MakeJsonOptions();

    private readonly Func<CancellationToken, ValueTask<string>> _token;
    private readonly TimeSpan _timeout;
    private readonly bool _retry;
    private readonly string _userAgent;
    private readonly RockwareHooks _hooks;
    private readonly HttpClient _http;
    private readonly string _url;

    /// <summary>Checks the options and makes a client. A bad setting throws RockwareException with Usage.</summary>
    public RockwareClient(RockwareOptions options)
    {
        if (options is null) throw new ArgumentNullException(nameof(options));
        Host = CheckHost(options.Host);
        _url = Host + "/graphql";
        if (options.TokenProvider is { } provider)
        {
            _token = provider;
        }
        else
        {
            if (string.IsNullOrWhiteSpace(options.Token)) throw new RockwareException(ErrorCode.Usage, "A token is required");
            var token = options.Token!;
            _token = _ => new ValueTask<string>(token);
        }
        if (options.Timeout <= TimeSpan.Zero) throw new RockwareException(ErrorCode.Usage, "Timeout must be more than 0");
        _timeout = options.Timeout;
        _retry = options.Retry;
        _userAgent = string.IsNullOrWhiteSpace(options.UserAgent) ? SdkAgent : $"{options.UserAgent!.Trim()} {SdkAgent}";
        _hooks = options.Hooks ?? new RockwareHooks();
        var handler = options.HttpHandler ?? new HttpClientHandler();
        if (handler is HttpClientHandler clientHandler) clientHandler.AllowAutoRedirect = false;
        _http = new HttpClient(handler, disposeHandler: options.HttpHandler is null) { Timeout = System.Threading.Timeout.InfiniteTimeSpan };
    }

    /// <summary>The host the client sends to.</summary>
    public string Host { get; }

    /// <summary>Lets go of the connection pool.</summary>
    public void Dispose() => _http.Dispose();

    /// <summary>Sends any operation from operations/ by name, and gives back its root field. The methods are easier; this is for tools.</summary>
    public Task<JsonElement> CallAsync(string name, IDictionary<string, object?>? variables = null, CancellationToken cancellationToken = default)
    {
        if (!Operations.All.TryGetValue(name, out var operation))
            throw new RockwareException(ErrorCode.Usage, "No operation named " + name);
        return RunAsync<JsonElement>(operation, variables ?? new Dictionary<string, object?>(), cancellationToken);
    }

    private async Task<T> RunAsync<T>(Operation operation, IDictionary<string, object?> variables, CancellationToken cancellationToken)
    {
        var token = await _token(cancellationToken).ConfigureAwait(false);
        if (string.IsNullOrWhiteSpace(token)) throw new RockwareException(ErrorCode.Usage, "A token is required");
        var sent = variables.Where(pair => pair.Value is not null).ToDictionary(pair => pair.Key, pair => pair.Value);
        string body;
        try
        {
            body = JsonSerializer.Serialize(
                new Dictionary<string, object?> { ["query"] = operation.Document, ["variables"] = sent, ["operationName"] = operation.Name },
                JsonOptions);
        }
        catch (Exception error) when (error is JsonException or NotSupportedException)
        {
            throw new RockwareException(ErrorCode.Usage, "Can't send these arguments: " + error.Message, error);
        }

        var attempts = _retry ? Behavior.Attempts : 1;
        for (var attempt = 1; ; attempt++)
        {
            var info = new RequestInfo(operation.Name, attempt, _url);
            Safely(() => _hooks.OnRequest?.Invoke(info));
            var started = DateTimeOffset.UtcNow;
            var (status, data, error) = await SendAsync(token, body, cancellationToken).ConfigureAwait(false);
            if (error is not null) error = Redact(error, token);
            Safely(() => _hooks.OnResponse?.Invoke(info, new ResponseInfo(status, DateTimeOffset.UtcNow - started, error)));
            if (error is null)
            {
                if (!data.TryGetProperty(operation.Root, out var root))
                    throw new RockwareException(ErrorCode.ApiError, "The server's answer has no " + operation.Root);
                try
                {
                    return JsonSerializer.Deserialize<T>(root.GetRawText(), JsonOptions)!;
                }
                catch (JsonException parse)
                {
                    throw new RockwareException(ErrorCode.ApiError, "Can't read the server's answer: " + parse.Message, parse);
                }
            }
            var delay = attempt < attempts ? RetryDelay(error, operation, attempt) : null;
            if (delay is null) throw error;
            Safely(() => _hooks.OnRetry?.Invoke(info, error, delay.Value));
            await Task.Delay(delay.Value, cancellationToken).ConfigureAwait(false);
        }
    }

    private async IAsyncEnumerable<T> PagesAsync<T>(
        Operation operation,
        Dictionary<string, object?> variables,
        int maxPages,
        [EnumeratorCancellation] CancellationToken cancellationToken)
    {
        if (maxPages < 1) throw new RockwareException(ErrorCode.Usage, "maxPages must be more than 0");
        var args = new Dictionary<string, object?>(variables);
        for (var page = 1; ; page++)
        {
            var connection = await RunAsync<Page<T>>(operation, args, cancellationToken).ConfigureAwait(false);
            foreach (var node in connection.Nodes) yield return node;
            var next = connection.PageInfo.EndCursor;
            if (!connection.PageInfo.HasNextPage || string.IsNullOrEmpty(next) || page >= maxPages) yield break;
            args["after"] = next;
        }
    }

    private sealed class Page<T>
    {
        [System.Text.Json.Serialization.JsonPropertyName("nodes")]
        public List<T> Nodes { get; set; } = new();

        [System.Text.Json.Serialization.JsonPropertyName("pageInfo")]
        public PageInfo PageInfo { get; set; } = new();
    }

    private sealed class PageInfo
    {
        [System.Text.Json.Serialization.JsonPropertyName("hasNextPage")]
        public bool HasNextPage { get; set; }

        [System.Text.Json.Serialization.JsonPropertyName("endCursor")]
        public string? EndCursor { get; set; }
    }

    private async Task<(int? Status, JsonElement Data, RockwareException? Error)> SendAsync(
        string token, string body, CancellationToken cancellationToken)
    {
        using var attempt = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        attempt.CancelAfter(_timeout);
        using var request = new HttpRequestMessage(HttpMethod.Post, _url)
        {
            Content = new StringContent(body, Encoding.UTF8, "application/json"),
        };
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        request.Headers.TryAddWithoutValidation("User-Agent", _userAgent);
        try
        {
            using var response = await _http.SendAsync(request, attempt.Token).ConfigureAwait(false);
            var text = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
            var (data, error) = ReadAnswer(response, text);
            return ((int)response.StatusCode, data, error);
        }
        catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
        {
            throw;
        }
        catch (Exception error) when (error is HttpRequestException or OperationCanceledException or System.IO.IOException)
        {
            var message = error is OperationCanceledException
                ? $"{Host} didn't answer within {_timeout.TotalSeconds:0.#} seconds"
                : $"Can't reach {Host}: {error.Message}";
            return (null, default, new RockwareException(ErrorCode.Network, message, error)
            {
                Retryable = true,
                Hint = RockwareException.HintFor(ErrorCode.Network, null),
            });
        }
    }

    private static (JsonElement Data, RockwareException? Error) ReadAnswer(HttpResponseMessage response, string text)
    {
        var status = (int)response.StatusCode;
        var requestId = response.Headers.TryGetValues("X-Request-Id", out var ids) ? ids.FirstOrDefault() : null;
        var retryAfter = ParseRetryAfter(response.Headers.RetryAfter);
        JsonElement? body = null;
        try
        {
            if (text.Length > 0) body = JsonDocument.Parse(text).RootElement;
        }
        catch (JsonException)
        {
        }

        var errors = new List<GraphQLError>();
        if (body is { ValueKind: JsonValueKind.Object } parsed &&
            parsed.TryGetProperty("errors", out var list) && list.ValueKind == JsonValueKind.Array)
        {
            errors = JsonSerializer.Deserialize<List<GraphQLError>>(list.GetRawText(), JsonOptions) ?? errors;
        }
        string? serverCode = null;
        if (errors.Count > 0 && errors[0].Extensions is { } extensions &&
            extensions.TryGetValue("code", out var code) && code.ValueKind == JsonValueKind.String)
        {
            serverCode = code.GetString();
        }
        var message = string.Join("; ", errors.Select(e => e.Message));

        RockwareException Fail(ErrorCode errorCode, string text, bool retryable = false, string? hint = null) =>
            new(errorCode, text)
            {
                HttpStatus = status,
                RequestId = requestId,
                RetryAfter = retryAfter,
                ServerCode = serverCode,
                Errors = errors,
                Retryable = retryable,
                Hint = hint,
            };

        if (status < 200 || status >= 300)
        {
            var errorCode = RockwareException.CodeForStatus(status);
            return (default, Fail(
                errorCode,
                message.Length > 0 ? message : $"The server answered HTTP {status}",
                retryable: errorCode == ErrorCode.RateLimit || status >= 500,
                hint: RockwareException.HintFor(errorCode, retryAfter)));
        }
        if (body is not { ValueKind: JsonValueKind.Object } answer)
            return (default, Fail(ErrorCode.ApiError, $"The server's answer isn't JSON (HTTP {status})"));
        if (errors.Count > 0)
        {
            var errorCode = RockwareException.CodeForServerCode(serverCode);
            return (default, Fail(errorCode, message, hint: RockwareException.HintFor(errorCode, null)));
        }
        if (!answer.TryGetProperty("data", out var data) || data.ValueKind != JsonValueKind.Object)
            return (default, Fail(ErrorCode.ApiError, "The server's answer has no data"));
        return (data, null);
    }

    private static TimeSpan? ParseRetryAfter(RetryConditionHeaderValue? header)
    {
        if (header?.Delta is { } delta) return delta;
        if (header?.Date is { } date)
        {
            var ahead = date - DateTimeOffset.UtcNow;
            if (ahead > TimeSpan.Zero) return TimeSpan.FromSeconds(Math.Ceiling(ahead.TotalSeconds));
        }
        return null;
    }

    /// <summary>How long to wait before trying again, or null to stop. SPEC.md section 5.</summary>
    private static TimeSpan? RetryDelay(RockwareException error, Operation operation, int attempt)
    {
        var refusedBeforeRunning = error.Code == ErrorCode.RateLimit;
        var mightHaveRun = error.Code == ErrorCode.Network || error.HttpStatus >= 500;
        if (!refusedBeforeRunning && !(mightHaveRun && operation.SafeToRepeat)) return null;
        if (error.RetryAfter is { } wait)
            return wait > TimeSpan.FromSeconds(Behavior.MaxRetryAfterSeconds) ? null : wait;
        var jitter = Jitter.NextDouble() * Behavior.MaxJitterMs;
        return TimeSpan.FromMilliseconds(Behavior.BaseDelayMs * Math.Pow(2, attempt - 1) + jitter);
    }

    private static readonly Random Jitter = new();

    private static RockwareException Redact(RockwareException error, string token)
    {
        if (!error.Message.Contains(token)) return error;
        return new RockwareException(error.Code, error.Message.Replace(token, "[hidden]"), error.InnerException)
        {
            Hint = error.Hint,
            HttpStatus = error.HttpStatus,
            Retryable = error.Retryable,
            RetryAfter = error.RetryAfter,
            RequestId = error.RequestId,
            ServerCode = error.ServerCode,
            Errors = error.Errors
                .Select(e => new GraphQLError { Message = e.Message.Replace(token, "[hidden]"), Path = e.Path, Extensions = e.Extensions })
                .ToList(),
        };
    }

    private static string CheckHost(string host)
    {
        if (!Uri.TryCreate(host, UriKind.Absolute, out var uri) || string.IsNullOrEmpty(uri.Host))
            throw new RockwareException(ErrorCode.Usage, "Host isn't a URL: " + host);
        if (uri.Scheme != Uri.UriSchemeHttps && !(uri.Scheme == Uri.UriSchemeHttp && uri.IsLoopback))
            throw new RockwareException(ErrorCode.Usage, "Host must use https://, except localhost");
        return host.TrimEnd('/');
    }

    private static void Safely(Action hook)
    {
        try
        {
            hook();
        }
        catch
        {
            // A hook's own failure never changes the call.
        }
    }

    private static JsonSerializerOptions MakeJsonOptions()
    {
        var options = new JsonSerializerOptions
        {
            // The server sends Decimal as a string, so no precision is lost.
            NumberHandling = System.Text.Json.Serialization.JsonNumberHandling.AllowReadingFromString,
        };
        options.Converters.Add(new InputObjectConverterFactory());
        return options;
    }
}
