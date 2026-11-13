// Made by scripts/generate.ts from the repo's schema/, operations/ and behavior.json. Don't edit it.

/** How to retry. SPEC.md section 5. */
export const RETRY = {
  "attempts": 3,
  "baseDelayMs": 1000,
  "maxJitterMs": 100,
  "maxRetryAfterSeconds": 60
} as const;
