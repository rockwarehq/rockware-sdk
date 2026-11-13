// The README's examples, so a change that breaks them fails typecheck.
import { type RockwareClient, RockwareError, parseWebhook } from "../src/index.js";

export async function examples(rockware: RockwareClient, secret: string, body: Uint8Array, header: string | undefined) {
  const site = await rockware.getSite();
  console.log(site?.name);
  const page = await rockware.listOrders({ first: 50 });
  console.log(page.nodes.length);
  let since: string | undefined;
  for await (const order of rockware.listAllOrders({ updatedSince: since })) since = order.updatedAt;
  const result = await rockware.upsertOrder({
    order: {
      externalId: "SO-1001",
      orderNumber: "1001",
      customer: { externalId: "C-42", name: "Globex" },
      lines: [{ product: "P-100", targetQuantity: 500 }],
    },
  });
  for (const error of result.errors) console.error(error.field, error.message);
  console.log(result.action, result.order?.id);
  try {
    await rockware.listProducts();
  } catch (error) {
    if (error instanceof RockwareError) console.error(error.code, error.hint, error.requestId);
  }
  const event = await parseWebhook(secret, body, header);
  if (event.data.object === "order") await rockware.getOrder({ id: event.data.id });
}
