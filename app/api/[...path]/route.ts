import { NextRequest } from "next/server";
export const dynamic = "force-dynamic";
async function proxy(request: NextRequest) {
  const base = process.env.PRIVATE_API_URL || "http://127.0.0.1:8000";
  const incoming = new URL(request.url);
  const target = new URL(incoming.pathname + incoming.search, base);
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("content-length");
  headers.delete("connection");
  if (process.env.PRIVATE_API_TOKEN)
    headers.set("x-internal-api-token", process.env.PRIVATE_API_TOKEN);
  try {
    const result = await fetch(target, {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method)
        ? undefined
        : await request.arrayBuffer(),
      redirect: "manual",
      cache: "no-store",
      signal: AbortSignal.timeout(120000),
    });
    const responseHeaders = new Headers(result.headers);
    responseHeaders.delete("content-encoding");
    responseHeaders.delete("content-length");
    return new Response(result.body, {
      status: result.status,
      headers: responseHeaders,
    });
  } catch {
    return Response.json(
      {
        detail:
          "Private processing service unavailable / ব্যক্তিগত প্রসেসিং সেবা পাওয়া যাচ্ছে না",
      },
      { status: 503 },
    );
  }
}
export {
  proxy as GET,
  proxy as POST,
  proxy as PATCH,
  proxy as DELETE,
  proxy as PUT,
};
