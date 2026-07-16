const CORE_API_URL = process.env.CORE_API_URL ?? "http://localhost:8000";

export async function coreApiFetch(path: string, init?: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5_000);
  try {
    return await fetch(`${CORE_API_URL}${path}`, {
      ...init,
      cache: "no-store",
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } finally {
    clearTimeout(timeout);
  }
}

export async function proxyCoreApi(path: string, init?: RequestInit): Promise<Response> {
  try {
    const upstream = await coreApiFetch(path, init);
    return new Response(await upstream.text(), {
      status: upstream.status,
      headers: { "Content-Type": upstream.headers.get("content-type") ?? "application/json" },
    });
  } catch {
    return Response.json({ error: "Core banking service is unavailable" }, { status: 503 });
  }
}
