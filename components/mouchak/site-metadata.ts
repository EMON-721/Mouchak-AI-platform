import type { Metadata } from "next";
import { defaultSite, type SiteSnapshot } from "./site-config";
/** Public config only, from the fixed operator-configured internal service. */
export async function siteMetadata(): Promise<Metadata> {
  let seo = defaultSite.seo;
  try {
    const base = process.env.PRIVATE_API_URL || "http://127.0.0.1:8000";
    if (
      process.env.NETLIFY &&
      (!base.startsWith("https://") || !process.env.PRIVATE_API_TOKEN)
    )
      return {
        title: seo.title_bn,
        description: seo.description_bn,
        robots: { index: false, follow: false },
      };
    const headers: Record<string, string> = {};
    if (process.env.PRIVATE_API_TOKEN)
      headers["x-internal-api-token"] = process.env.PRIVATE_API_TOKEN;
    const response = await fetch(new URL("/api/public/site", base), {
      headers,
      cache: "no-store",
      signal: AbortSignal.timeout(2000),
    });
    if (response.ok) seo = ((await response.json()) as SiteSnapshot).config.seo;
  } catch {
    /* Built-in public metadata when the backend is unavailable. */
  }
  return {
    title: { default: seo.title_bn, template: `%s · ${seo.title_en}` },
    description: seo.description_bn,
    robots: { index: seo.index, follow: seo.index },
  };
}
