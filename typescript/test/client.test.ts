// What the shared tests don't cover: hooks, token functions, stopping a call,
// and parseWebhook.

import { describe, expect, it } from "vitest";
import { RockwareClient, RockwareError, parseWebhook } from "../src/index.js";

const site = { data: { site: { id: "site_1" } } };

function answering(...answers: Array<() => Response>) {
  const tokens: string[] = [];
  let i = 0;
  const fetch: typeof globalThis.fetch = async (_url, init) => {
    tokens.push(new Headers(init?.headers).get("authorization") ?? "");
    const answer = answers[i++];
    if (!answer) throw new Error("no more answers");
    return answer();
  };
  return { fetch, tokens };
}

describe("RockwareClient", () => {
  it("asks a token function for the token on each call", async () => {
    let n = 0;
    const { fetch, tokens } = answering(
      () => Response.json(site),
      () => Response.json(site),
    );
    const client = new RockwareClient({
      host: "https://acme-api.example.com",
      token: async () => `rw_app_${++n}`,
      fetch,
    });
    await client.getSite();
    await client.getSite();
    expect(tokens).toEqual(["Bearer rw_app_1", "Bearer rw_app_2"]);
  });

  it("calls the hooks, and a hook that throws changes nothing", async () => {
    const seen: string[] = [];
    const { fetch } = answering(
      () => new Response(null, { status: 503 }),
      () => Response.json(site),
    );
    const client = new RockwareClient({
      host: "https://acme-api.example.com",
      token: "rw_app_test",
      fetch,
      hooks: {
        onRequest: (info) => {
          seen.push(`request ${info.operation} ${info.attempt}`);
          throw new Error("a broken hook");
        },
        onResponse: (info, result) =>
          seen.push(`response ${info.attempt} ${result.httpStatus} ${result.error?.code ?? "ok"}`),
        onRetry: (info, error, delayMs) => seen.push(`retry ${info.attempt} ${error.code} ${delayMs >= 1000}`),
      },
    });
    expect(await client.getSite()).toEqual({ id: "site_1" });
    expect(seen).toEqual([
      "request GetSite 1",
      "response 1 503 api_error",
      "retry 1 api_error true",
      "request GetSite 2",
      "response 2 200 ok",
    ]);
  }, 10_000);

  it("stops waiting to retry when the signal aborts", async () => {
    const { fetch } = answering(() => new Response(null, { status: 503 }));
    const client = new RockwareClient({ host: "https://acme-api.example.com", token: "rw_app_test", fetch });
    const controller = new AbortController();
    setTimeout(() => controller.abort(new Error("stopped")), 50);
    await expect(client.getSite({ signal: controller.signal })).rejects.toThrow("stopped");
  });

  it("refuses a bad host when it's made", () => {
    expect(() => new RockwareClient({ host: "not a url", token: "rw_app_test" })).toThrow(RockwareError);
  });

  it("can send any operation by name", async () => {
    const { fetch } = answering(() => Response.json(site));
    const client = new RockwareClient({ host: "https://acme-api.example.com", token: "rw_app_test", fetch });
    expect(await client.call("GetSite")).toEqual({ id: "site_1" });
  });
});

describe("parseWebhook", () => {
  const body =
    '{"id":"evt_1","type":"order.updated","occurredAt":"2026-11-09T15:00:00.000Z","siteId":"site_1","data":{"object":"order","id":"ord_1"}}';
  const header = "t=1700000000,v1=236c14c5656906da5cdf38cecc494968b3b4c55aeef1d83818a866f6e046d75e";

  it("gives back the event when the signature is right", async () => {
    const event = await parseWebhook("whsec_test", body, header, { now: 1700000000 });
    expect(event).toMatchObject({ id: "evt_1", type: "order.updated", data: { object: "order", id: "ord_1" } });
  });

  it("takes the body as bytes too", async () => {
    const event = await parseWebhook("whsec_test", new TextEncoder().encode(body), header, { now: 1700000000 });
    expect(event.id).toBe("evt_1");
  });

  it("fails with forbidden when the signature is wrong", async () => {
    await expect(parseWebhook("whsec_other", body, header, { now: 1700000000 })).rejects.toMatchObject({
      code: "forbidden",
    });
  });
});
