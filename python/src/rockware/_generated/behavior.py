# Made by scripts/generate.py from the repo's schema/, operations/ and behavior.json. Don't edit it.

"""How to retry. SPEC.md section 5."""

RETRY: dict[str, int] = {"attempts": 3, "baseDelayMs": 1000, "maxJitterMs": 100, "maxRetryAfterSeconds": 60}
