using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Rockware;

/// <summary>What Rockware sends: ids only. Fetch the record to see what changed.</summary>
public sealed class WebhookEvent
{
    /// <summary>Skip an id you've already handled: the same event can arrive twice.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = "";

    /// <summary>Like "order.updated".</summary>
    [JsonPropertyName("type")]
    public string Type { get; set; } = "";

    /// <summary>When it happened.</summary>
    [JsonPropertyName("occurredAt")]
    public DateTimeOffset OccurredAt { get; set; }

    /// <summary>The plant.</summary>
    [JsonPropertyName("siteId")]
    public string SiteId { get; set; } = "";

    /// <summary>The record that changed.</summary>
    [JsonPropertyName("data")]
    public WebhookEventData Data { get; set; } = new();
}

/// <summary>The record a webhook event is about.</summary>
public sealed class WebhookEventData
{
    /// <summary>What kind of record, like "order".</summary>
    [JsonPropertyName("object")]
    public string Object { get; set; } = "";

    /// <summary>Its id in Rockware.</summary>
    [JsonPropertyName("id")]
    public string Id { get; set; } = "";
}

/// <summary>Checks webhook deliveries. SPEC.md section 7.</summary>
public static class RockwareWebhooks
{
    /// <summary>The header that carries the signature.</summary>
    public const string SignatureHeader = "Rockware-Signature";

    /// <summary>The header that carries the event's id.</summary>
    public const string EventIdHeader = "Rockware-Event-Id";

    /// <summary>The header that carries the event's type.</summary>
    public const string EventTypeHeader = "Rockware-Event-Type";

    private static readonly TimeSpan DefaultTolerance = TimeSpan.FromMinutes(5);

    /// <summary>
    /// True when the Rockware-Signature header signs this body, and its time is
    /// within <paramref name="tolerance"/> of now (default 5 minutes). Pass the raw body as it arrived.
    /// </summary>
    public static bool Verify(string secret, byte[] rawBody, string? header, TimeSpan? tolerance = null, DateTimeOffset? now = null)
    {
        if (string.IsNullOrEmpty(secret) || string.IsNullOrEmpty(header) || rawBody is null) return false;
        var parts = new Dictionary<string, string>();
        foreach (var part in header!.Split(','))
        {
            var at = part.IndexOf('=');
            if (at > 0) parts[part.Substring(0, at).Trim()] = part.Substring(at + 1).Trim();
        }
        if (!parts.TryGetValue("t", out var t) || !parts.TryGetValue("v1", out var v1)) return false;
        if (t.Length == 0 || !IsDigits(t) || !long.TryParse(t, out var signed) || v1.Length != 64) return false;
        var given = new byte[32];
        for (var i = 0; i < 32; i++)
        {
            var high = HexValue(v1[i * 2]);
            var low = HexValue(v1[i * 2 + 1]);
            if (high < 0 || low < 0) return false;
            given[i] = (byte)((high << 4) | low);
        }
        var current = (now ?? DateTimeOffset.UtcNow).ToUnixTimeSeconds();
        if (Math.Abs(current - signed) > (long)(tolerance ?? DefaultTolerance).TotalSeconds) return false;

        var prefix = Encoding.UTF8.GetBytes(t + ".");
        var signedBytes = new byte[prefix.Length + rawBody.Length];
        Buffer.BlockCopy(prefix, 0, signedBytes, 0, prefix.Length);
        Buffer.BlockCopy(rawBody, 0, signedBytes, prefix.Length, rawBody.Length);
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret));
        var expected = hmac.ComputeHash(signedBytes);

        // Constant time: look at every byte, whatever the first difference.
        var difference = 0;
        for (var i = 0; i < expected.Length; i++) difference |= expected[i] ^ given[i];
        return difference == 0;
    }

    /// <inheritdoc cref="Verify(string, byte[], string?, TimeSpan?, DateTimeOffset?)"/>
    public static bool Verify(string secret, string rawBody, string? header, TimeSpan? tolerance = null, DateTimeOffset? now = null) =>
        Verify(secret, Encoding.UTF8.GetBytes(rawBody ?? ""), header, tolerance, now);

    /// <summary>Checks the signature, then reads the event. Throws RockwareException with Forbidden if the signature is wrong or too old.</summary>
    public static WebhookEvent Parse(string secret, byte[] rawBody, string? header, TimeSpan? tolerance = null, DateTimeOffset? now = null)
    {
        if (!Verify(secret, rawBody, header, tolerance, now))
            throw new RockwareException(ErrorCode.Forbidden, "The webhook's signature is wrong or too old");
        try
        {
            return JsonSerializer.Deserialize<WebhookEvent>(rawBody, RockwareClient.JsonOptions)
                ?? throw new JsonException("empty");
        }
        catch (JsonException error)
        {
            throw new RockwareException(ErrorCode.Validation, "The webhook's body isn't JSON", error);
        }
    }

    /// <inheritdoc cref="Parse(string, byte[], string?, TimeSpan?, DateTimeOffset?)"/>
    public static WebhookEvent Parse(string secret, string rawBody, string? header, TimeSpan? tolerance = null, DateTimeOffset? now = null) =>
        Parse(secret, Encoding.UTF8.GetBytes(rawBody ?? ""), header, tolerance, now);

    private static bool IsDigits(string text)
    {
        foreach (var c in text)
            if (c < '0' || c > '9') return false;
        return true;
    }

    private static int HexValue(char c) =>
        c >= '0' && c <= '9' ? c - '0' : c >= 'a' && c <= 'f' ? c - 'a' + 10 : c >= 'A' && c <= 'F' ? c - 'A' + 10 : -1;
}
