// What newer .NET has built in, so `required` and `init` also compile for
// netstandard2.0. Internal, so nothing leaks to callers.

#if !NET7_0_OR_GREATER
namespace System.Runtime.CompilerServices
{
    internal sealed class RequiredMemberAttribute : Attribute { }

    internal sealed class CompilerFeatureRequiredAttribute : Attribute
    {
        public CompilerFeatureRequiredAttribute(string featureName) => FeatureName = featureName;

        public string FeatureName { get; }
    }

    internal static class IsExternalInit { }
}

namespace System.Diagnostics.CodeAnalysis
{
    [AttributeUsage(AttributeTargets.Constructor)]
    internal sealed class SetsRequiredMembersAttribute : Attribute { }
}
#endif
