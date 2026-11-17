using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Rockware;

/// <summary>
/// Something sent to the API, like an order. Only the properties you set are
/// sent: a field you leave alone is left as it is. Setting one to null sends
/// null, which clears that field.
/// </summary>
public abstract class InputObject
{
    private readonly Dictionary<string, object?> _values = new();

    /// <summary>Gets a field's value, or the default if it isn't set.</summary>
    protected T Get<T>(string name) => _values.TryGetValue(name, out var value) && value is T typed ? typed : default!;

    /// <summary>Sets a field, so it's sent.</summary>
    protected void Set(string name, object? value) => _values[name] = value;

    /// <summary>Whether a field is set, by its name in the API, like "dueDate".</summary>
    public bool IsSet(string name) => _values.ContainsKey(name);

    /// <summary>Unsets a field by its name in the API, so it isn't sent.</summary>
    public void Unset(string name) => _values.Remove(name);

    internal IEnumerable<KeyValuePair<string, object?>> SetFields => _values;
}

/// <summary>Writes only an input's set fields, and reads one back.</summary>
internal sealed class InputObjectConverterFactory : JsonConverterFactory
{
    public override bool CanConvert(Type typeToConvert) => typeof(InputObject).IsAssignableFrom(typeToConvert);

    public override JsonConverter CreateConverter(Type typeToConvert, JsonSerializerOptions options) =>
        (JsonConverter)Activator.CreateInstance(typeof(InputObjectConverter<>).MakeGenericType(typeToConvert))!;
}

internal sealed class InputObjectConverter<T> : JsonConverter<T>
    where T : InputObject
{
    private static readonly ConcurrentDictionary<string, PropertyInfo> Properties = new(
        typeof(T).GetProperties()
            .Select(p => (Property: p, Name: p.GetCustomAttribute<JsonPropertyNameAttribute>()?.Name))
            .Where(p => p.Name != null)
            .ToDictionary(p => p.Name!, p => p.Property)
    );

    public override T Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        if (reader.TokenType != JsonTokenType.StartObject) throw new JsonException($"{typeof(T).Name} must be an object");
        var input = (T)Activator.CreateInstance(typeof(T))!;
        while (reader.Read() && reader.TokenType != JsonTokenType.EndObject)
        {
            var name = reader.GetString()!;
            reader.Read();
            if (Properties.TryGetValue(name, out var property))
                property.SetValue(input, JsonSerializer.Deserialize(ref reader, property.PropertyType, options));
            else
                reader.Skip();
        }
        return input;
    }

    public override void Write(Utf8JsonWriter writer, T value, JsonSerializerOptions options)
    {
        writer.WriteStartObject();
        foreach (var pair in value.SetFields)
        {
            writer.WritePropertyName(pair.Key);
            JsonSerializer.Serialize(writer, pair.Value, pair.Value?.GetType() ?? typeof(object), options);
        }
        writer.WriteEndObject();
    }
}
