// Runs the repo's shared tests (conformance/) against this SDK. A fake HTTP
// handler plays the server. See conformance/README.md for the format.

using System.Net;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using Xunit;

namespace Rockware.Tests;

public class ConformanceTests
{
    private static string Conformance([CallerFilePath] string here = "") =>
        Path.GetFullPath(Path.Combine(Path.GetDirectoryName(here)!, "..", "..", "..", "conformance"));

    public static IEnumerable<object[]> Cases() =>
        Directory.GetFiles(Path.Combine(Conformance(), "tests"), "*.json")
            .OrderBy(f => f)
            .SelectMany(file => JsonDocument.Parse(File.ReadAllText(file)).RootElement.EnumerateArray()
                .Select(test => new object[] { $"{Path.GetFileNameWithoutExtension(file)}: {test.GetProperty("name").GetString()}", test.GetRawText() }));

    private sealed record Sent(DateTime At, string Method, string Url, HttpRequestMessage Request, JsonElement Body);

    private sealed class FakeServer(JsonElement answers) : HttpMessageHandler
    {
        public List<Sent> Requests { get; } = new();

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            var body = JsonDocument.Parse(await request.Content!.ReadAsStringAsync(cancellationToken)).RootElement;
            lock (Requests) Requests.Add(new Sent(DateTime.UtcNow, request.Method.Method, request.RequestUri!.ToString(), request, body));
            if (Requests.Count > answers.GetArrayLength()) throw new InvalidOperationException($"The test has no answer for request {Requests.Count}");
            var answer = answers[Requests.Count - 1];
            if (answer.TryGetProperty("networkError", out var dropped) && dropped.GetBoolean()) throw new HttpRequestException("connection dropped");
            var status = answer.TryGetProperty("status", out var s) ? s.GetInt32() : 200;
            var content = answer.TryGetProperty("rawBody", out var raw) ? raw.GetString()!
                : answer.TryGetProperty("body", out var json) ? json.GetRawText() : "";
            var response = new HttpResponseMessage((HttpStatusCode)status) { Content = new StringContent(content, Encoding.UTF8) };
            if (answer.TryGetProperty("headers", out var headers))
                foreach (var header in headers.EnumerateObject())
                    response.Headers.TryAddWithoutValidation(header.Name, Resolve(header.Value.GetString()!));
            return response;
        }

        private static string Resolve(string value) =>
            Regex.Replace(value, @"\{\{httpdate\+(\d{1,9})s\}\}", m =>
                DateTimeOffset.FromUnixTimeSeconds(DateTimeOffset.UtcNow.ToUnixTimeSeconds() + long.Parse(m.Groups[1].Value) + 1).ToString("r"));
    }

    private static JsonElement? At(JsonElement value, string path)
    {
        if (path == "") return value;
        var current = value;
        foreach (var key in path.Split('.'))
        {
            if (current.ValueKind == JsonValueKind.Array)
            {
                if (key == "length") current = JsonSerializer.SerializeToElement(current.GetArrayLength());
                else if (int.TryParse(key, out var i) && i < current.GetArrayLength()) current = current[i];
                else return null;
            }
            else if (current.ValueKind == JsonValueKind.Object && current.TryGetProperty(key, out var next)) current = next;
            else return null;
        }
        return current;
    }

    private static bool Same(JsonElement? a, JsonElement b) =>
        a is { } x && JsonSerializer.Serialize(Normalize(x)) == JsonSerializer.Serialize(Normalize(b));

    private static object? Normalize(JsonElement e) => e.ValueKind switch
    {
        JsonValueKind.Number => e.GetDouble(),
        JsonValueKind.Object => e.EnumerateObject().OrderBy(p => p.Name).ToDictionary(p => p.Name, p => Normalize(p.Value)),
        JsonValueKind.Array => e.EnumerateArray().Select(Normalize).ToList(),
        JsonValueKind.String => e.GetString(),
        JsonValueKind.True => true,
        JsonValueKind.False => false,
        _ => null,
    };

    [Theory]
    [MemberData(nameof(Cases))]
    public async Task Conformance_(string name, string json)
    {
        _ = name;
        var test = JsonDocument.Parse(json).RootElement;
        var server = new FakeServer(test.GetProperty("responses"));
        var client = test.TryGetProperty("client", out var c) ? c : default;
        string? Setting(string key) => client.ValueKind == JsonValueKind.Object && client.TryGetProperty(key, out var v) ? v.GetString() : null;
        var vars = test.TryGetProperty("variables", out var v) ? v : JsonDocument.Parse("{}").RootElement;
        var paginate = test.TryGetProperty("paginate", out var p) && p.GetBoolean();
        var maxPages = test.TryGetProperty("maxPages", out var m) ? m.GetInt32() : RockwareClient.DefaultMaxPages;
        var operation = test.GetProperty("operation").GetString()!;

        object? result = null;
        var collected = new List<object>();
        Exception? error = null;
        try
        {
            using var rockware = new RockwareClient(new RockwareOptions
            {
                Host = Setting("host") ?? "https://acme-api.example.com",
                Token = Setting("token") ?? "rw_app_test",
                UserAgent = Setting("userAgent"),
                Retry = !(client.ValueKind == JsonValueKind.Object && client.TryGetProperty("retry", out var r) && !r.GetBoolean()),
                HttpHandler = server,
            });
            if (paginate)
                await foreach (var record in Dispatch.Pages[operation](rockware, vars, maxPages)) collected.Add(record);
            else
                result = await Dispatch.Calls[operation](rockware, vars);
        }
        catch (Exception caught)
        {
            error = caught;
        }
        var resultJson = JsonSerializer.SerializeToElement(paginate ? collected : result, ResultOptions);
        var rw = error as RockwareException;
        var sent = server.Requests;

        foreach (var a in test.GetProperty("assertions").EnumerateArray())
        {
            var kind = a.GetProperty("type").GetString();
            var index = a.TryGetProperty("index", out var ix) ? ix.GetInt32() : 0;
            bool Has(string key, out JsonElement value) => a.TryGetProperty(key, out value);
            switch (kind)
            {
                case "requestCount":
                    Assert.Equal(a.GetProperty("expected").GetInt32(), sent.Count);
                    break;
                case "requestMethod":
                    Assert.Equal(a.GetProperty("expected").GetString(), sent[0].Method);
                    break;
                case "requestUrl":
                    Assert.Equal(a.GetProperty("expected").GetString(), sent[0].Url);
                    break;
                case "requestHeader":
                {
                    var request = sent[index].Request;
                    var headerName = a.GetProperty("name").GetString()!;
                    var values = request.Headers.TryGetValues(headerName, out var h) ? h
                        : request.Content!.Headers.TryGetValues(headerName, out var ch) ? ch : null;
                    // .NET keeps User-Agent as parts; on the wire they're joined by spaces.
                    var value = headerName.Equals("user-agent", StringComparison.OrdinalIgnoreCase)
                        ? request.Headers.UserAgent.ToString()
                        : values is null ? null : string.Join(", ", values);
                    if (Has("expected", out var expected)) Assert.Equal(expected.GetString(), value);
                    if (Has("pattern", out var pattern)) Assert.Matches(pattern.GetString()!, value ?? "");
                    break;
                }
                case "requestBody":
                {
                    var path = a.GetProperty("path").GetString()!;
                    var value = At(sent[index].Body, path);
                    if (Has("absent", out var absent) && absent.GetBoolean()) Assert.True(value is null, $"{path} should be left out");
                    if (Has("expected", out var expected)) Assert.True(Same(value, expected), $"{path}: got {value}, want {expected}");
                    if (Has("pattern", out var pattern)) Assert.Matches(pattern.GetString()!, value?.ToString() ?? "");
                    if (Has("expectedInstant", out var instant))
                        Assert.Equal(DateTimeOffset.Parse(instant.GetString()!), DateTimeOffset.Parse(value!.Value.GetString()!));
                    break;
                }
                case "delayBetweenRequests":
                {
                    var gap = (sent[index + 1].At - sent[index].At).TotalMilliseconds;
                    Assert.True(gap >= a.GetProperty("minMs").GetDouble(), $"gap {gap}ms");
                    if (Has("maxMs", out var most)) Assert.True(gap <= most.GetDouble(), $"gap {gap}ms");
                    break;
                }
                case "noError":
                    Assert.Null(error);
                    break;
                case "error":
                    Assert.NotNull(rw);
                    if (Has("code", out var code)) Assert.Equal(code.GetString(), Snake(rw!.Code.ToString()));
                    if (Has("httpStatus", out var status)) Assert.Equal(status.GetInt32(), rw!.HttpStatus);
                    if (Has("retryable", out var retryable)) Assert.Equal(retryable.GetBoolean(), rw!.Retryable);
                    if (Has("retryAfter", out var after)) Assert.Equal(after.GetDouble(), rw!.RetryAfter?.TotalSeconds);
                    if (Has("requestId", out var id)) Assert.Equal(id.GetString(), rw!.RequestId);
                    if (Has("serverCode", out var serverCode)) Assert.Equal(serverCode.GetString(), rw!.ServerCode);
                    break;
                case "errorMessage":
                    Assert.NotNull(rw);
                    if (Has("pattern", out var messagePattern)) Assert.Matches(messagePattern.GetString()!, rw!.Message);
                    if (Has("excludes", out var excludes)) Assert.DoesNotContain(excludes.GetString()!, rw!.Message);
                    break;
                case "errorMessageLength":
                    Assert.True(rw!.Message.Length <= a.GetProperty("max").GetInt32());
                    break;
                case "errorCount":
                    Assert.Equal(a.GetProperty("expected").GetInt32(), rw!.Errors.Count);
                    break;
                case "result":
                {
                    var path = a.GetProperty("path").GetString()!;
                    var value = At(resultJson, path);
                    var expected = a.GetProperty("expected");
                    var ok = expected.ValueKind == JsonValueKind.Null ? value is null || value.Value.ValueKind == JsonValueKind.Null : Same(value, expected);
                    Assert.True(ok, $"result {path}: got {value}, want {expected}");
                    break;
                }
                default:
                    throw new InvalidOperationException("Unknown assertion type " + kind);
            }
        }
    }

    // The fake server's records leave fields out, which a real answer never
    // does. A JSON value that was never set is written as null.
    private static readonly JsonSerializerOptions ResultOptions = new(RockwareClient.JsonOptions)
    {
        Converters = { new UnsetJsonElementAsNull() },
    };

    private sealed class UnsetJsonElementAsNull : System.Text.Json.Serialization.JsonConverter<JsonElement>
    {
        public override JsonElement Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options) =>
            JsonElement.ParseValue(ref reader);

        public override void Write(Utf8JsonWriter writer, JsonElement value, JsonSerializerOptions options)
        {
            if (value.ValueKind == JsonValueKind.Undefined) writer.WriteNullValue();
            else value.WriteTo(writer);
        }
    }

    private static string Snake(string pascal) => Regex.Replace(pascal, "(?<=[a-z])([A-Z])", "_$1").ToLowerInvariant();

    public static IEnumerable<object[]> WebhookCases() =>
        JsonDocument.Parse(File.ReadAllText(Path.Combine(Conformance(), "webhooks.json"))).RootElement.GetProperty("cases").EnumerateArray()
            .Select(c => new object[] { c.GetProperty("name").GetString()!, c.GetRawText() });

    [Theory]
    [MemberData(nameof(WebhookCases))]
    public void WebhookSignature(string name, string json)
    {
        var c = JsonDocument.Parse(json).RootElement;
        var tolerance = c.TryGetProperty("tolerance", out var t) ? TimeSpan.FromSeconds(t.GetInt32()) : (TimeSpan?)null;
        var valid = RockwareWebhooks.Verify(
            c.GetProperty("secret").GetString()!, c.GetProperty("body").GetString()!, c.GetProperty("header").GetString(),
            tolerance, DateTimeOffset.FromUnixTimeSeconds(c.GetProperty("now").GetInt64()));
        Assert.True(c.GetProperty("valid").GetBoolean() == valid, name);
    }
}
