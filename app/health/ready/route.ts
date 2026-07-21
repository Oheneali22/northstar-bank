import { coreApiFetch } from "../../lib/core-api";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const response = await coreApiFetch("/health/ready");
    if (!response.ok) throw new Error("Core API is not ready");
    return Response.json({ status: "ready", service: "northstar-web" });
  } catch {
    return Response.json(
      { status: "not_ready", service: "northstar-web", dependency: "core-api" },
      { status: 503 },
    );
  }
}
