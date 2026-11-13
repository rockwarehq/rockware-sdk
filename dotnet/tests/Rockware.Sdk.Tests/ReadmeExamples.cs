// The README's examples, so a change that breaks them fails to compile. Not run.

using Rockware;

namespace Rockware.Tests;

internal static class ReadmeExamples
{
    public static async Task Start(string token)
    {
        using var rockware = new RockwareClient(new RockwareOptions
        {
            Host = "https://acme-api.rockware.io",
            Token = token,
            UserAgent = "acme-erp-sync/1.0",
        });
        var site = await rockware.GetSiteAsync();
        Console.WriteLine(site?.Name);

        var page = await rockware.ListOrdersAsync(first: 50);
        Console.WriteLine(page.Nodes.Count);

        await foreach (var product in rockware.ListAllProductsAsync())
            Console.WriteLine($"{product.Sku} {product.Name}");

        var since = DateTimeOffset.UtcNow.AddDays(-1);
        await foreach (var order in rockware.ListAllOrdersAsync(updatedSince: since))
            since = order.UpdatedAt;

        var result = await rockware.UpsertOrderAsync(new OrderInput
        {
            ExternalId = "SO-1001",
            OrderNumber = "1001",
            Customer = new CustomerInput { ExternalId = "C-42", Name = "Globex" },
            Lines = new List<OrderLineInput> { new() { Product = "P-100", TargetQuantity = 500 } },
        });
        if (result.Errors.Count > 0)
        {
            foreach (var problem in result.Errors) Console.WriteLine($"{problem.Field} {problem.Message}");
        }
        else
        {
            Console.WriteLine($"{result.Action} {result.Order?.Id}");
        }

        await rockware.UpsertOrderAsync(new OrderInput { ExternalId = "SO-1001", Notes = null });

        try
        {
            await rockware.ListProductsAsync();
        }
        catch (RockwareException error)
        {
            Console.WriteLine($"{error.Code} {error.Message} {error.Hint} {error.RequestId}");
        }
    }

    public static void Webhook(string secret, byte[] body, string? header)
    {
        var webhookEvent = RockwareWebhooks.Parse(secret, body, header);
        Console.WriteLine($"{webhookEvent.Id} {webhookEvent.Type} {webhookEvent.Data.Object} {webhookEvent.Data.Id}");
    }
}
