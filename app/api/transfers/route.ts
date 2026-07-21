import { proxyCoreApi } from "../../lib/core-api";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const accountId = new URL(request.url).searchParams.get("account_id");
  const query = accountId ? `?account_id=${encodeURIComponent(accountId)}` : "";
  return proxyCoreApi(`/api/v1/transfers${query}`);
}

export async function POST(request: Request) {
  const key = request.headers.get("idempotency-key") ?? crypto.randomUUID();
  return proxyCoreApi("/api/v1/transfers", {
    method: "POST",
    body: await request.text(),
    headers: { "Idempotency-Key": key },
  });
}
