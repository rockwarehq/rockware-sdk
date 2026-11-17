// What the shared tests don't cover: inputs you do and don't set, decimals,
// hooks, token providers, calls by name, and parsing webhooks.

using System.Net;
using System.Text;
using System.Text.Json;
using Xunit;

namespace Rockware.Tests;

public class ClientTests
{
    private sealed class Answering(params string[] bodies) : HttpMessageHandler
    {
        public List<string> Bodies { get; } = new();
        public List<string?> Tokens { get; } = new();

        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            Bodies.Add(await request.Content!.ReadAsStringAsync(cancellationToken));
            Tokens.Add(request.Headers.Authorization?.ToString());
            var body = bodies[Bodies.Count - 1];
            return body.Length == 0
                ? new HttpResponseMessage(HttpStatusCode.ServiceUnavailable)
                : new HttpResponseMessage(HttpStatusCode.OK) { Content = new StringContent(body, Encoding.UTF8, "application/json") };
        }
    }

    private static RockwareClient Client(HttpMessageHandler handler, RockwareHooks? hooks = null) =>
        new(new RockwareOptions { Host = "https://acme-api.example.com", Token = "rw_app_test", HttpHandler = handler, Hooks = hooks });

    private const string Unchanged = """{"data":{"upsertOrder":{"action":"UNCHANGED","order":null,"errors":[]}}}""";

    [Fact]
    public async Task OnlyTheFieldsYouSetAreSent_AndNullClearsOne()
    {
        var server = new Answering(Unchanged);
        using var rockware = Client(server);
        await rockware.UpsertOrderAsync(new OrderInput { ExternalId = "SO-1", Notes = null, PoNumber = "PO-9" });
        var order = JsonDocument.Parse(server.Bodies[0]).RootElement.GetProperty("variables").GetProperty("order");
        Assert.Equal("""{"externalId":"SO-1","notes":null,"poNumber":"PO-9"}""", order.GetRawText());
        Assert.False(JsonDocument.Parse(server.Bodies[0]).RootElement.GetProperty("variables").TryGetProperty("source", out _));
    }

    [Fact]
    public async Task DecimalsAreExact()
    {
        var server = new Answering("""{"data":{"product":{"id":"p1","itemCost":"12.3456789012345678","weight":null,"externalIds":[],"createdAt":"2026-11-01T00:00:00.000Z","updatedAt":"2026-11-01T00:00:00.000Z"}}}""");
        using var rockware = Client(server);
        var product = await rockware.GetProductAsync("p1");
        Assert.Equal(12.3456789012345678m, product!.ItemCost);
        Assert.Null(product.Weight);
        Assert.Equal(new DateTimeOffset(2026, 11, 1, 0, 0, 0, TimeSpan.Zero), product.CreatedAt);
    }

    [Fact]
    public async Task HooksAreCalled_AndOneThatThrowsChangesNothing()
    {
        var seen = new List<string>();
        var hooks = new RockwareHooks
        {
            OnRequest = info =>
            {
                seen.Add($"request {info.Operation} {info.Attempt}");
                throw new InvalidOperationException("a broken hook");
            },
            OnResponse = (info, result) => seen.Add($"response {info.Attempt} {result.HttpStatus} {result.Error?.Code.ToString() ?? "ok"}"),
            OnRetry = (info, error, delay) => seen.Add($"retry {info.Attempt} {error.Code} {delay >= TimeSpan.FromSeconds(1)}"),
        };
        using var rockware = Client(new Answering("", """{"data":{"site":{"id":"site_1","name":"Plant","timezone":"UTC","updatedAt":"2026-11-01T00:00:00Z"}}}"""), hooks);
        var site = await rockware.GetSiteAsync();
        Assert.Equal("site_1", site!.Id);
        Assert.Equal(new[] { "request GetSite 1", "response 1 503 ApiError", "retry 1 ApiError True", "request GetSite 2", "response 2 200 ok" }, seen);
    }

    [Fact]
    public async Task ATokenProviderIsAskedOnEachCall()
    {
        var server = new Answering("""{"data":{"site":null}}""", """{"data":{"site":null}}""");
        var n = 0;
        using var rockware = new RockwareClient(new RockwareOptions
        {
            Host = "https://acme-api.example.com",
            TokenProvider = _ => new ValueTask<string>($"rw_app_{++n}"),
            HttpHandler = server,
        });
        await rockware.GetSiteAsync();
        await rockware.GetSiteAsync();
        Assert.Equal(new[] { "Bearer rw_app_1", "Bearer rw_app_2" }, server.Tokens);
    }

    [Fact]
    public async Task AnyOperationCanBeSentByName()
    {
        using var rockware = Client(new Answering("""{"data":{"site":{"id":"site_1"}}}"""));
        var site = await rockware.CallAsync("GetSite");
        Assert.Equal("site_1", site.GetProperty("id").GetString());
        var error = await Assert.ThrowsAsync<RockwareException>(() => rockware.CallAsync("Nope"));
        Assert.Equal(ErrorCode.Usage, error.Code);
    }

    private const string EventBody = """{"id":"evt_1","type":"order.updated","occurredAt":"2026-11-09T15:00:00.000Z","siteId":"site_1","data":{"object":"order","id":"ord_1"}}""";
    private const string EventHeader = "t=1700000000,v1=236c14c5656906da5cdf38cecc494968b3b4c55aeef1d83818a866f6e046d75e";

    [Fact]
    public void ParseWebhookGivesBackTheEvent()
    {
        var webhookEvent = RockwareWebhooks.Parse("whsec_test", EventBody, EventHeader, now: DateTimeOffset.FromUnixTimeSeconds(1700000000));
        Assert.Equal("evt_1", webhookEvent.Id);
        Assert.Equal("order", webhookEvent.Data.Object);
        Assert.Equal("ord_1", webhookEvent.Data.Id);
    }

    [Fact]
    public void ParseWebhookRefusesAWrongSignature()
    {
        var error = Assert.Throws<RockwareException>(() =>
            RockwareWebhooks.Parse("whsec_other", EventBody, EventHeader, now: DateTimeOffset.FromUnixTimeSeconds(1700000000)));
        Assert.Equal(ErrorCode.Forbidden, error.Code);
    }
}
