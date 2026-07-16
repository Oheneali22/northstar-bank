import { proxyCoreApi } from "../../lib/core-api";

export const dynamic = "force-dynamic";

export async function GET() {
  return proxyCoreApi("/api/v1/accounts");
}
