namespace Rockware;

/// <summary>One operation from operations/, ready to send.</summary>
public sealed class Operation
{
    internal Operation(string name, string root, bool mutation, bool safeToRepeat, string document)
    {
        Name = name;
        Root = root;
        Mutation = mutation;
        SafeToRepeat = safeToRepeat;
        Document = document;
    }

    /// <summary>The operation's name, like GetProduct.</summary>
    public string Name { get; }

    /// <summary>The one field it asks for. Its value is what the method returns.</summary>
    public string Root { get; }

    /// <summary>Whether it's a mutation.</summary>
    public bool Mutation { get; }

    /// <summary>Sending it twice gives the same result as once, so it can be retried.</summary>
    public bool SafeToRepeat { get; }

    /// <summary>The operation and the fragments it uses.</summary>
    public string Document { get; }
}
