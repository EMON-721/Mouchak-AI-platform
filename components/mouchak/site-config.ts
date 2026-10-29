import defaults from "@/packages/ui-tokens/site-defaults.json";
import type { Tool } from "./types";
export type Bilingual = { bn: string; en: string };
export type MenuItem = Bilingual & { href: string };
export type FieldCopy = Bilingual & {
  help_bn?: string;
  help_en?: string;
  placeholder_bn?: string;
  placeholder_en?: string;
};
export type ToolCopy = {
  name?: Bilingual | null;
  description?: Bilingual | null;
  logo_asset?: string | null;
  fields: Record<string, FieldCopy>;
};
export type SiteConfig = {
  schema_version: 1;
  brand: {
    name_bn: string;
    name_en: string;
    tagline_bn: string;
    tagline_en: string;
    logo_asset: string | null;
    favicon_asset: string | null;
  };
  theme: {
    light: Record<string, string>;
    dark: Record<string, string>;
    font: "bengali_sans" | "system_serif";
    text_scale: number;
  };
  navigation: MenuItem[];
  footer: { text: Bilingual; note: Bilingual; links: MenuItem[] };
  home: {
    sections: string[];
    featured_slugs: string[];
    text: Record<string, Bilingual>;
    faqs: { question: Bilingual; answer: Bilingual }[];
  };
  category_labels: Record<string, Bilingual>;
  tool_overrides: Record<string, ToolCopy>;
  pages: Record<string, { title: Bilingual; body: Bilingual }>;
  locales: Record<string, Bilingual>;
  seo: {
    title_bn: string;
    title_en: string;
    description_bn: string;
    description_en: string;
    index: boolean;
  };
};
export type SiteSnapshot = { revision: string | null; config: SiteConfig };
export const defaultSite = defaults as SiteConfig;
export const siteAssetUrl = (id: string) =>
  "/api/public/site-assets/" + id + ".svg";
export function customizeTool(
  tool: Tool,
  site: SiteConfig,
  lang: "bn" | "en",
): Tool {
  if (tool.presentation_base) tool = { ...tool, ...tool.presentation_base };
  const patch = site.tool_overrides[tool.slug];
  if (!patch) return tool;
  return {
    ...tool,
    name: patch.name?.[lang] || tool.name,
    description_bn: patch.description?.bn || tool.description_bn,
    description_en: patch.description?.en || tool.description_en,
    logo: patch.logo_asset ? siteAssetUrl(patch.logo_asset) : tool.logo,
    fields: tool.fields?.map((f) => ({
      ...f,
      ...patch.fields[f.key],
      columns: f.columns?.map((c) => ({
        ...c,
        ...patch.fields[f.key + "." + c.key],
      })),
    })),
  };
}
export function siteTokenCSS(site: SiteConfig) {
  const palette = (values: Record<string, string>) =>
    Object.keys(defaultSite.theme.light)
      .map((key) => {
        const value = values[key];
        return /^#[a-f0-9]{6}$/i.test(value) ? `--${key}:${value};` : "";
      })
      .join("");
  const scale = Number.isFinite(site.theme.text_scale)
    ? Math.min(1.2, Math.max(1, site.theme.text_scale))
    : 1;
  const font =
    site.theme.font === "system_serif"
      ? '"Noto Bengali", Georgia, serif'
      : '"Noto Bengali", Arial, sans-serif';
  return `:root{${palette(site.theme.light)}font-size:${16 * scale}px}:root[data-theme="dark"]{${palette(site.theme.dark)}}:root[data-large="true"]{font-size:${19 * scale}px}body{font-family:${font};font-size:calc(.9375rem)}`;
}
