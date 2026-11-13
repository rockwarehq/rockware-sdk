// Checking webhook deliveries. SPEC.md section 7.
//
// Uses Web Crypto, so it runs the same in Node, Deno, Bun and edge workers.

import { RockwareError } from "./errors.js";

export const SIGNATURE_HEADER = "Rockware-Signature";
export const EVENT_ID_HEADER = "Rockware-Event-Id";
export const EVENT_TYPE_HEADER = "Rockware-Event-Type";

export interface VerifyOptions {
  /** How far the signed time may be from now, in seconds. Default 300. */
  tolerance?: number;
  /** Now, in unix seconds. For tests. */
  now?: number;
}

/** What Rockware sends: ids only. Fetch the record to see what changed. */
export interface WebhookEvent {
  /** Skip an id you've already handled: the same event can arrive twice. */
  id: string;
  /** Like "order.updated". */
  type: string;
  occurredAt: string;
  siteId: string;
  data: { object: string; id: string };
}

const encoder = new TextEncoder();

/**
 * True when the Rockware-Signature header signs this body, and its time is
 * within the tolerance. Pass the raw body as it arrived, before parsing.
 */
export async function verifyWebhook(
  secret: string,
  rawBody: string | Uint8Array,
  header: string | null | undefined,
  options: VerifyOptions = {},
): Promise<boolean> {
  if (!secret || !header) return false;
  const parts = new Map<string, string>();
  for (const part of header.split(",")) {
    const at = part.indexOf("=");
    if (at > 0) parts.set(part.slice(0, at).trim(), part.slice(at + 1).trim());
  }
  const t = parts.get("t");
  const v1 = parts.get("v1");
  if (!t || !/^\d+$/.test(t) || !v1 || !/^[0-9a-fA-F]{64}$/.test(v1)) return false;

  const now = options.now ?? Math.floor(Date.now() / 1000);
  if (Math.abs(now - Number(t)) > (options.tolerance ?? 300)) return false;

  const body = typeof rawBody === "string" ? encoder.encode(rawBody) : rawBody;
  const prefix = encoder.encode(`${t}.`);
  const signed = new Uint8Array(prefix.length + body.length);
  signed.set(prefix);
  signed.set(body, prefix.length);

  const key = await crypto.subtle.importKey("raw", encoder.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, [
    "sign",
  ]);
  const expected = new Uint8Array(await crypto.subtle.sign("HMAC", key, signed));
  const given = new Uint8Array(v1.length / 2);
  for (let i = 0; i < given.length; i++) given[i] = Number.parseInt(v1.slice(i * 2, i * 2 + 2), 16);

  // Constant time: look at every byte, whatever the first difference.
  let difference = expected.length ^ given.length;
  for (let i = 0; i < expected.length; i++) difference |= (expected[i] ?? 0) ^ (given[i] ?? 0);
  return difference === 0;
}

/** Check the signature, then read the event. Fails with code "forbidden" if the signature is wrong. */
export async function parseWebhook(
  secret: string,
  rawBody: string | Uint8Array,
  header: string | null | undefined,
  options: VerifyOptions = {},
): Promise<WebhookEvent> {
  if (!(await verifyWebhook(secret, rawBody, header, options))) {
    throw new RockwareError("forbidden", "The webhook's signature is wrong or too old");
  }
  const text = typeof rawBody === "string" ? rawBody : new TextDecoder().decode(rawBody);
  try {
    return JSON.parse(text) as WebhookEvent;
  } catch (cause) {
    throw new RockwareError("validation", "The webhook's body isn't JSON", { cause });
  }
}
