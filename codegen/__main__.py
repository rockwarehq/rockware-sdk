import sys

USAGE = "Usage: python -m codegen go|dotnet"

if len(sys.argv) != 2:
    sys.exit(USAGE)
if sys.argv[1] == "go":
    from .go import main
elif sys.argv[1] == "dotnet":
    from .dotnet import main
else:
    sys.exit(USAGE)
main()
