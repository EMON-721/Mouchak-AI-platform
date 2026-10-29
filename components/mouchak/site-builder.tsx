"use client";
import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import Image from "next/image";
import { siteAssetUrl } from "./site-config";
import { useApp } from "./context";
import { Home } from "./catalogue";
import {
  type Bilingual,
  type FieldCopy,
  type MenuItem,
  type SiteConfig,
  type SiteSnapshot,
  type ToolCopy,
} from "./site-config";

type Version = {
  id: string;
  status: string;
  author: string;
  created_at: string;
};
type Blueprint = {
  slug: string;
  name: string;
  description_bn: string;
  description_en: string;
  fields: Record<string, { bn: string; en: string; type: string }>;
};
type EditorState = {
  active: SiteSnapshot;
  defaults: SiteConfig;
  editable_locales: string[];
  categories: string[];
  tools: Blueprint[];
  assets: {
    id: string;
    license_uri: string;
    rights_note: string;
    created_at: string;
  }[];
  versions: Version[];
};
type Pane =
  | "brand"
  | "theme"
  | "navigation"
  | "home"
  | "pages"
  | "tools"
  | "locales"
  | "seo"
  | "versions"
  | "json";
const panes: [Pane, string, string][] = [
  ["brand", "ব্র্যান্ড ও লোগো", "Brand & marks"],
  ["theme", "রং ও অক্ষর", "Theme & type"],
  ["navigation", "মেনু ও ফুটার", "Navigation & footer"],
  ["home", "হোমপেজ", "Homepage"],
  ["pages", "তথ্য পাতা", "Public pages"],
  ["tools", "৫০ টুলের লেখা", "50 tool labels"],
  ["locales", "ভাষা ও বিভাগ", "Language & categories"],
  ["seo", "সার্চ পরিচিতি", "Search metadata"],
  ["versions", "সংস্করণ ও প্রকাশ", "Review & publish"],
  ["json", "JSON সম্পাদনা", "Advanced JSON"],
];
function CopyEditor({
  label,
  value,
  onChange,
  area = false,
}: {
  label: string;
  value: Bilingual;
  onChange: (v: Bilingual) => void;
  area?: boolean;
}) {
  const { t } = useApp();
  return (
    <fieldset className="site-copy">
      <legend>{label}</legend>
      {(["bn", "en"] as const).map((lang) => (
        <label className="form-field" key={lang}>
          {lang === "bn" ? "বাংলা" : "English"}
          {area ? (
            <textarea
              rows={3}
              maxLength={12000}
              value={value[lang]}
              onChange={(e) => onChange({ ...value, [lang]: e.target.value })}
            />
          ) : (
            <input
              maxLength={4000}
              value={value[lang]}
              onChange={(e) => onChange({ ...value, [lang]: e.target.value })}
            />
          )}
        </label>
      ))}
      <small className="subtle">
        {t("দুই ভাষাতেই লেখা দিন।", "Provide both languages.")}
      </small>
    </fieldset>
  );
}
function LinksEditor({
  label,
  links,
  onChange,
}: {
  label: string;
  links: MenuItem[];
  onChange: (v: MenuItem[]) => void;
}) {
  const { t } = useApp();
  return (
    <fieldset className="site-copy">
      <legend>{label}</legend>
      {links.map((link, i) => (
        <div className="panel" key={i}>
          <CopyEditor
            label={t("লিংকের নাম", "Link label")}
            value={link}
            onChange={(v) =>
              onChange(links.map((x, j) => (i === j ? { ...x, ...v } : x)))
            }
          />
          <label className="form-field">
            {t("সাইটের পাথ", "Existing public path")}
            <input
              value={link.href}
              onChange={(e) =>
                onChange(
                  links.map((x, j) =>
                    i === j ? { ...x, href: e.target.value } : x,
                  ),
                )
              }
            />
          </label>
          <div className="button-row">
            <button
              type="button"
              disabled={i === 0}
              className="button outline small"
              onClick={() => {
                const next = [...links];
                [next[i - 1], next[i]] = [next[i], next[i - 1]];
                onChange(next);
              }}
            >
              {t("উপরে", "Move up")}
            </button>
            <button
              type="button"
              className="button outline small"
              onClick={() => onChange(links.filter((_, j) => j !== i))}
            >
              {t("সরান", "Remove")}
            </button>
          </div>
        </div>
      ))}
      <button
        type="button"
        className="button outline small"
        onClick={() =>
          onChange([
            ...links,
            { bn: "নতুন লিংক", en: "New link", href: "/about" },
          ])
        }
      >
        {t("লিংক যোগ করুন", "Add link")}
      </button>
      <p>
        {t(
          "শুধু বিদ্যমান public পাথ গ্রহণযোগ্য। Explore এবং footer-এর Privacy/Terms রাখতে হবে।",
          "Only existing public paths are accepted. Keep Explore and the footer’s Privacy/Terms links.",
        )}
      </p>
    </fieldset>
  );
}
function ensureTool(config: SiteConfig, slug: string): ToolCopy {
  return (config.tool_overrides[slug] ||= { fields: {} });
}
function Notice({ children }: { children: ReactNode }) {
  return <p className="notice">{children}</p>;
}

export function SiteBuilderEditor() {
  const { api, t, user, refreshSite } = useApp();
  const [state, setState] = useState<EditorState | null>(null),
    [draft, setDraft] = useState<SiteConfig | null>(null),
    [draftBaseRevision, setDraftBaseRevision] = useState<string | null>(null),
    [pane, setPane] = useState<Pane>("brand"),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  const [slug, setSlug] = useState("pukursos-ai"),
    [page, setPage] = useState("about"),
    [reason, setReason] = useState(""),
    [due, setDue] = useState(""),
    [preview, setPreview] = useState(""),
    [width, setWidth] = useState(390),
    [raw, setRaw] = useState("");
  const [svg, setSvg] = useState(""),
    [license, setLicense] = useState(""),
    [rights, setRights] = useState(""),
    [attest, setAttest] = useState(false);
  useEffect(() => {
    let live = true;
    api<EditorState>("/api/admin/site-builder")
      .then((value) => {
        if (live) {
          setState(value);
          setDraft(structuredClone(value.active.config));
          setDraftBaseRevision(value.active.revision);
        }
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [api, user?.id]);
  async function reload(reset = false) {
    const value = await api<EditorState>("/api/admin/site-builder");
    setState(value);
    if (reset) {
      setDraft(structuredClone(value.active.config));
      setDraftBaseRevision(value.active.revision);
    }
    return value;
  }
  async function action(work: () => Promise<unknown>, success: string) {
    if (busy) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await work();
      setMessage(success);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function edit(update: (value: SiteConfig) => void) {
    setDraft((previous) => {
      if (!previous) return previous;
      const next = structuredClone(previous);
      update(next);
      return next;
    });
    setMessage("");
  }
  const failure = error ? (
    <div className="error" role="alert">
      {error}
      {error === "MFA_REQUIRED" ? (
        <p>
          <Link href="/admin/security">
            {t("আগে MFA যাচাই করুন", "Verify MFA first")}
          </Link>
        </p>
      ) : null}
    </div>
  ) : null;
  if (!state || !draft)
    return (
      <>
        {failure}
        <p>{t("সাইটের সেটিংস লোড হচ্ছে…", "Loading site configuration…")}</p>
      </>
    );
  const selected = state.tools.find((x) => x.slug === slug)!;
  const tool = draft.tool_overrides[slug];
  const assetOptions = (
    <>
      <option value="">{t("মূল লোগো / ডিফল্ট", "Original / default")}</option>
      {state.assets.map((a) => (
        <option key={a.id} value={a.id}>
          {a.id.slice(0, 12)} · {a.created_at.slice(0, 10)}
        </option>
      ))}
    </>
  );
  const chosenPage = draft.pages[page] || {
    title: { bn: "", en: "" },
    body: { bn: "", en: "" },
  };
  return (
    <section className="site-builder">
      <div className="section-heading">
        <div>
          <p className="eyebrow">MOUCHAK SITE BUILDER</p>
          <h1>
            {t(
              "সাইট সাজান, যাচাই করে প্রকাশ করুন।",
              "Edit, review and publish your site.",
            )}
          </h1>
          <p>
            {t(
              "এখানকার পরিবর্তন ড্রাফট হিসেবে থাকে। আলাদা সম্পাদক অনুমোদন দিলে প্রকাশ করা যাবে।",
              "Edits stay private drafts until another editor approves the exact version.",
            )}
          </p>
        </div>
        <Link href="/admin/security" className="button outline small">
          MFA
        </Link>
      </div>
      {failure}
      {message ? (
        <p className="success" role="status">
          {message}
        </p>
      ) : null}
      <nav
        className="site-tabs"
        aria-label={t("সাইট সম্পাদনার অংশ", "Site editor sections")}
      >
        {panes.map(([key, bn, en]) => (
          <button
            type="button"
            aria-pressed={pane === key}
            className={pane === key ? "selected" : ""}
            key={key}
            onClick={() => {
              setPane(key);
              if (key === "json") setRaw(JSON.stringify(draft, null, 2));
            }}
          >
            {t(bn, en)}
          </button>
        ))}
      </nav>
      <div className="panel site-edit-panel" aria-busy={busy}>
        {pane === "brand" ? (
          <>
            <h2>
              {t(
                "পরিচিতি ও নিজস্ব ব্র্যান্ড চিহ্ন",
                "Identity and owned brand marks",
              )}
            </h2>
            <CopyEditor
              label={t("সাইটের নাম", "Site name")}
              value={{ bn: draft.brand.name_bn, en: draft.brand.name_en }}
              onChange={(v) =>
                edit((c) => {
                  c.brand.name_bn = v.bn;
                  c.brand.name_en = v.en;
                })
              }
            />
            <CopyEditor
              label={t("ছোট পরিচিতি", "Tagline")}
              value={{ bn: draft.brand.tagline_bn, en: draft.brand.tagline_en }}
              onChange={(v) =>
                edit((c) => {
                  c.brand.tagline_bn = v.bn;
                  c.brand.tagline_en = v.en;
                })
              }
            />
            {(["logo_asset", "favicon_asset"] as const).map((key) => (
              <label className="form-field" key={key}>
                {key === "logo_asset"
                  ? t("মূল লোগো", "Brand logo")
                  : t("ব্রাউজারের আইকন", "Favicon")}
                <select
                  value={draft.brand[key] || ""}
                  onChange={(e) =>
                    edit((c) => {
                      c.brand[key] = e.target.value || null;
                    })
                  }
                >
                  {assetOptions}
                </select>
              </label>
            ))}
            <details>
              <summary>
                {t(
                  "সংরক্ষিত চিহ্ন ও অনুমতির বিবরণ",
                  "Saved artwork and rights declarations",
                )}
              </summary>
              {state.assets.length ? (
                state.assets.map((asset) => (
                  <article className="panel" key={asset.id}>
                    <Image
                      unoptimized
                      src={siteAssetUrl(asset.id)}
                      width={64}
                      height={64}
                      alt={t("সংরক্ষিত ব্র্যান্ড চিহ্ন", "Saved brand artwork")}
                    />
                    <p>
                      <code>{asset.id}</code>
                    </p>
                    <p>{asset.rights_note}</p>
                    <a
                      className="text-link"
                      href={asset.license_uri}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {t("ঘোষিত লাইসেন্স দেখুন", "Inspect declared licence")} ↗
                    </a>
                    <p>{asset.created_at}</p>
                  </article>
                ))
              ) : (
                <p>
                  {t("কোনো চিহ্ন যোগ করা হয়নি।", "No artwork has been added.")}
                </p>
              )}
            </details>
            <details>
              <summary>
                {t("নিজস্ব SVG যোগ করুন", "Add owned SVG artwork")}
              </summary>
              <Notice>
                {t(
                  "শুধু স্থির geometric SVG, ৩০ KB পর্যন্ত। script, image, URL, style বা ব্যক্তিগত upload গ্রহণ করা হয় না। এই অনুমতি কেবল সাইটের প্রকাশ্য ব্র্যান্ড চিহ্নের জন্য।",
                  "Static geometric SVG only, up to 30 KB. Scripts, images, URLs, styles and private uploads are refused. This permission covers public brand artwork only.",
                )}
              </Notice>
              <label className="form-field">
                SVG
                <textarea
                  rows={6}
                  maxLength={30000}
                  value={svg}
                  onChange={(e) => setSvg(e.target.value)}
                />
              </label>
              <label className="form-field">
                {t("অথবা SVG ফাইল পড়ুন", "Or read an SVG file")}
                <input
                  type="file"
                  accept=".svg,image/svg+xml"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      if (file.size > 30000) {
                        setError(
                          t("ফাইল ৩০ KB-এর বেশি।", "File exceeds 30 KB."),
                        );
                        return;
                      }
                      setSvg(await file.text());
                    }
                  }}
                />
              </label>
              <label className="form-field">
                {t("লাইসেন্সের HTTPS লিংক", "HTTPS licence link")}
                <input
                  type="url"
                  value={license}
                  onChange={(e) => setLicense(e.target.value)}
                />
              </label>
              <label className="form-field">
                {t(
                  "মালিকানা ও ব্যবহারের অনুমতি",
                  "Ownership and permitted use",
                )}
                <textarea
                  minLength={20}
                  maxLength={2000}
                  value={rights}
                  onChange={(e) => setRights(e.target.value)}
                />
              </label>
              <label className="consent-row">
                <input
                  type="checkbox"
                  checked={attest}
                  onChange={(e) => setAttest(e.target.checked)}
                />
                {t(
                  "এই চিহ্ন প্রকাশের অধিকার আমার আছে।",
                  "I have the right to publish this artwork.",
                )}
              </label>
              <button
                disabled={busy || !attest}
                type="button"
                className="button outline"
                onClick={() =>
                  action(
                    async () => {
                      await api("/api/admin/site-assets", {
                        method: "POST",
                        body: JSON.stringify({
                          svg,
                          license_uri: license,
                          rights_note: rights,
                          attest_rights: attest,
                        }),
                      });
                      await reload();
                      setSvg("");
                      setAttest(false);
                    },
                    t(
                      "চিহ্নটি ব্যক্তিগত সংগ্রহে যোগ হয়েছে; প্রকাশ এখনো হয়নি।",
                      "Artwork added privately; it is not published yet.",
                    ),
                  )
                }
              >
                {t("চিহ্ন যাচাই করে যোগ করুন", "Validate & add artwork")}
              </button>
            </details>
          </>
        ) : null}
        {pane === "theme" ? (
          <>
            <h2>
              {t("পঠনযোগ্য রং ও অক্ষর", "Readable colours and typography")}
            </h2>
            <Notice>
              {t(
                "দুই theme-এ মূল লেখার contrast কমপক্ষে 4.5:1 থাকতে হবে। ভুল contrast হলে সার্ভার ড্রাফট নেবে না।",
                "Core text needs at least 4.5:1 contrast in both themes. The server refuses failing palettes.",
              )}
            </Notice>
            {(["light", "dark"] as const).map((mode) => (
              <fieldset className="site-palette" key={mode}>
                <legend>
                  {mode === "light"
                    ? t("হালকা রং", "Light theme")
                    : t("গাঢ় রং", "Dark theme")}
                </legend>
                {Object.entries(draft.theme[mode]).map(([key, value]) => (
                  <label className="form-field" key={key}>
                    {key}
                    <input
                      type="color"
                      value={value}
                      onChange={(e) =>
                        edit((c) => {
                          c.theme[mode][key] = e.target.value;
                        })
                      }
                    />
                    <code>{value}</code>
                  </label>
                ))}
              </fieldset>
            ))}
            <label className="form-field">
              {t("অক্ষরের ধরন", "Font family")}
              <select
                value={draft.theme.font}
                onChange={(e) =>
                  edit((c) => {
                    c.theme.font = e.target
                      .value as SiteConfig["theme"]["font"];
                  })
                }
              >
                <option value="bengali_sans">বাংলা Sans</option>
                <option value="system_serif">বাংলা + Serif</option>
              </select>
            </label>
            <label className="form-field">
              {t("অক্ষরের আকার", "Text scale")}
              <input
                type="range"
                min="1"
                max="1.2"
                step="0.05"
                value={draft.theme.text_scale}
                onChange={(e) =>
                  edit((c) => {
                    c.theme.text_scale = Number(e.target.value);
                  })
                }
              />
              {draft.theme.text_scale.toFixed(2)}×
            </label>
          </>
        ) : null}
        {pane === "navigation" ? (
          <>
            <LinksEditor
              label={t("প্রধান মেনু", "Main menu")}
              links={draft.navigation}
              onChange={(v) =>
                edit((c) => {
                  c.navigation = v;
                })
              }
            />
            <CopyEditor
              label={t("ফুটারের পরিচিতি", "Footer introduction")}
              value={draft.footer.text}
              onChange={(v) =>
                edit((c) => {
                  c.footer.text = v;
                })
              }
              area
            />
            <CopyEditor
              label={t("ফুটারের নোট", "Footer note")}
              value={draft.footer.note}
              onChange={(v) =>
                edit((c) => {
                  c.footer.note = v;
                })
              }
            />
            <LinksEditor
              label={t("ফুটারের লিংক", "Footer links")}
              links={draft.footer.links}
              onChange={(v) =>
                edit((c) => {
                  c.footer.links = v;
                })
              }
            />
          </>
        ) : null}
        {pane === "home" ? (
          <>
            <h2>
              {t("হোমপেজের লেখা ও বিন্যাস", "Homepage text and section order")}
            </h2>
            {Object.entries(draft.home.text).map(([key, value]) => (
              <CopyEditor
                key={key}
                label={key}
                value={value}
                area={key === "hero_intro"}
                onChange={(v) =>
                  edit((c) => {
                    c.home.text[key] = v;
                  })
                }
              />
            ))}
            <fieldset className="site-copy">
              <legend>{t("অংশের ক্রম", "Section order")}</legend>
              {draft.home.sections.map((key, i) => (
                <div className="button-row" key={key}>
                  <strong>{key}</strong>
                  <button
                    type="button"
                    className="button outline small"
                    disabled={i <= 1}
                    onClick={() =>
                      edit((c) => {
                        [c.home.sections[i - 1], c.home.sections[i]] = [
                          c.home.sections[i],
                          c.home.sections[i - 1],
                        ];
                      })
                    }
                  >
                    {t("উপরে", "Move up")}
                  </button>
                  <button
                    type="button"
                    className="button outline small"
                    disabled={key === "hero" || key === "principles"}
                    onClick={() =>
                      edit((c) => {
                        c.home.sections = c.home.sections.filter(
                          (x) => x !== key,
                        );
                      })
                    }
                  >
                    {t("সরান", "Remove")}
                  </button>
                </div>
              ))}
              <label className="form-field">
                {t("অংশ যোগ করুন", "Add section")}
                <select
                  value=""
                  onChange={(e) => {
                    if (e.target.value)
                      edit((c) => {
                        c.home.sections.push(e.target.value);
                      });
                  }}
                >
                  <option value="">{t("বেছে নিন", "Choose")}</option>
                  {["statement", "featured", "faq", "closing"]
                    .filter((x) => !draft.home.sections.includes(x))
                    .map((x) => (
                      <option key={x}>{x}</option>
                    ))}
                </select>
              </label>
            </fieldset>
            <fieldset className="site-copy">
              <legend>
                {t("শুরুর টুলগুলো: ১–৮টি", "Featured tools: 1–8")}
              </legend>
              {state.tools.map((x) => (
                <label className="site-check" key={x.slug}>
                  <input
                    type="checkbox"
                    checked={draft.home.featured_slugs.includes(x.slug)}
                    onChange={(e) =>
                      edit((c) => {
                        c.home.featured_slugs = e.target.checked
                          ? [...c.home.featured_slugs, x.slug]
                          : c.home.featured_slugs.filter((s) => s !== x.slug);
                      })
                    }
                  />
                  {x.name}
                </label>
              ))}
            </fieldset>
            <h3>FAQ</h3>
            {draft.home.faqs.map((faq, i) => (
              <div className="panel" key={i}>
                <CopyEditor
                  label={t("প্রশ্ন", "Question")}
                  value={faq.question}
                  onChange={(v) =>
                    edit((c) => {
                      c.home.faqs[i].question = v;
                    })
                  }
                />
                <CopyEditor
                  label={t("উত্তর", "Answer")}
                  value={faq.answer}
                  onChange={(v) =>
                    edit((c) => {
                      c.home.faqs[i].answer = v;
                    })
                  }
                  area
                />
                <button
                  className="button outline small"
                  type="button"
                  onClick={() =>
                    edit((c) => {
                      c.home.faqs.splice(i, 1);
                    })
                  }
                >
                  {t("সরান", "Remove")}
                </button>
              </div>
            ))}
            <button
              className="button outline small"
              type="button"
              disabled={draft.home.faqs.length >= 12}
              onClick={() =>
                edit((c) => {
                  c.home.faqs.push({
                    question: { bn: "নতুন প্রশ্ন", en: "New question" },
                    answer: { bn: "উত্তর লিখুন", en: "Enter the answer" },
                  });
                })
              }
            >
              {t("প্রশ্ন যোগ করুন", "Add question")}
            </button>
          </>
        ) : null}
        {pane === "pages" ? (
          <>
            <h2>{t("প্রকাশ্য তথ্য পাতা", "Public information pages")}</h2>
            <label className="form-field">
              {t("পাতা বাছুন", "Choose page")}
              <select value={page} onChange={(e) => setPage(e.target.value)}>
                {[
                  "about",
                  "methodology",
                  "help",
                  "privacy",
                  "terms",
                  "contact",
                ].map((x) => (
                  <option key={x}>{x}</option>
                ))}
              </select>
            </label>
            <Notice>
              {t(
                "লেখা plain text। নতুন override-এর দুই ভাষা পূরণ করুন। override সরালে আগের প্রকাশিত বা মূল লেখা ফিরবে। আইনগত ও সেবার দাবি নিজে পর্যালোচনা করুন।",
                "Content is plain text. Complete both languages for a new override. Removing an override restores earlier CMS or built-in content. Review legal and service claims carefully.",
              )}
            </Notice>
            <CopyEditor
              label={t("শিরোনাম", "Title")}
              value={chosenPage.title}
              onChange={(v) =>
                edit((c) => {
                  c.pages[page] = { ...chosenPage, title: v };
                })
              }
            />
            <CopyEditor
              label={t("মূল লেখা", "Body")}
              value={chosenPage.body}
              area
              onChange={(v) =>
                edit((c) => {
                  c.pages[page] = { ...chosenPage, body: v };
                })
              }
            />
            <button
              className="button outline small"
              type="button"
              onClick={() =>
                edit((c) => {
                  delete c.pages[page];
                })
              }
            >
              {t("এই পাতার override সরান", "Remove this page override")}
            </button>
          </>
        ) : null}
        {pane === "tools" ? (
          <>
            <h2>
              {t(
                "টুলের পরিচিতি, field label ও সহায়ক লেখা",
                "Tool identity, field labels and help",
              )}
            </h2>
            <Notice>
              {t(
                "ইনপুটের নিয়ম, model, safety, consent, readiness বা data access বদলানো যায় না। নতুন নামেও স্থায়ী tool ID একই থাকবে।",
                "Input rules, models, safety, consent, readiness and data access cannot be changed here. A renamed tool keeps its permanent ID.",
              )}
            </Notice>
            <label className="form-field">
              {t("টুল বাছুন", "Choose tool")}
              <select value={slug} onChange={(e) => setSlug(e.target.value)}>
                {state.tools.map((x) => (
                  <option key={x.slug} value={x.slug}>
                    {x.name}
                  </option>
                ))}
              </select>
            </label>
            <code>{slug}</code>
            <CopyEditor
              label={t("প্রদর্শনের নাম", "Display name")}
              value={tool?.name || { bn: selected.name, en: selected.name }}
              onChange={(v) =>
                edit((c) => {
                  ensureTool(c, slug).name = v;
                })
              }
            />
            <CopyEditor
              label={t("ছোট বিবরণ", "Short description")}
              value={
                tool?.description || {
                  bn: selected.description_bn,
                  en: selected.description_en,
                }
              }
              area
              onChange={(v) =>
                edit((c) => {
                  ensureTool(c, slug).description = v;
                })
              }
            />
            <label className="form-field">
              {t("টুলের নিজস্ব লোগো", "Tool logo")}
              <select
                value={tool?.logo_asset || ""}
                onChange={(e) =>
                  edit((c) => {
                    ensureTool(c, slug).logo_asset = e.target.value || null;
                  })
                }
              >
                {assetOptions}
              </select>
            </label>
            {Object.entries(selected.fields).map(([key, baseline]) => {
              const value: FieldCopy = tool?.fields[key] || {
                bn: baseline.bn,
                en: baseline.en,
              };
              return (
                <details key={key}>
                  <summary>
                    {key} · {t(value.bn, value.en)}
                  </summary>
                  <CopyEditor
                    label={t("ঘরের নাম", "Field label")}
                    value={value}
                    onChange={(v) =>
                      edit((c) => {
                        ensureTool(c, slug).fields[key] = { ...value, ...v };
                      })
                    }
                  />
                  <CopyEditor
                    label={t("সহায়ক লেখা", "Help text")}
                    value={{ bn: value.help_bn || "", en: value.help_en || "" }}
                    area
                    onChange={(v) =>
                      edit((c) => {
                        ensureTool(c, slug).fields[key] = {
                          ...value,
                          help_bn: v.bn,
                          help_en: v.en,
                        };
                      })
                    }
                  />
                  <CopyEditor
                    label={t("ঘরে দেখানো নমুনা", "Placeholder")}
                    value={{
                      bn: value.placeholder_bn || "",
                      en: value.placeholder_en || "",
                    }}
                    onChange={(v) =>
                      edit((c) => {
                        ensureTool(c, slug).fields[key] = {
                          ...value,
                          placeholder_bn: v.bn,
                          placeholder_en: v.en,
                        };
                      })
                    }
                  />
                  <button
                    type="button"
                    className="button outline small"
                    onClick={() =>
                      edit((c) => {
                        delete ensureTool(c, slug).fields[key];
                      })
                    }
                  >
                    {t("ঘরের মূল লেখা ফিরিয়ে আনুন", "Restore field text")}
                  </button>
                </details>
              );
            })}
            <button
              type="button"
              className="button outline small"
              onClick={() =>
                edit((c) => {
                  delete c.tool_overrides[slug];
                })
              }
            >
              {t(
                "এই টুলের সব override সরান",
                "Remove all overrides for this tool",
              )}
            </button>
          </>
        ) : null}
        {pane === "locales" ? (
          <>
            <h2>
              {t(
                "নির্দিষ্ট UI লেখা ও বিভাগ",
                "Approved UI labels and categories",
              )}
            </h2>
            <Notice>
              {t(
                "সক্ষমতা, নিরাপত্তা ও সম্মতির ঘোষণা এই তালিকায় নেই। খালি override সরাতে Restore চাপুন।",
                "Readiness, safety and consent statements are excluded. Use Restore to remove a label override.",
              )}
            </Notice>
            {[
              ["category_labels", state.categories],
              ["locales", state.editable_locales],
            ].map(([section, keys]) => (
              <details key={section as string}>
                <summary>{section as string}</summary>
                {(keys as string[]).map((key) => {
                  const map = section as "category_labels" | "locales";
                  return (
                    <div key={key}>
                      <CopyEditor
                        label={key}
                        value={draft[map][key] || { bn: "", en: key }}
                        onChange={(v) =>
                          edit((c) => {
                            c[map][key] = v;
                          })
                        }
                      />
                      <button
                        type="button"
                        className="button outline small"
                        onClick={() =>
                          edit((c) => {
                            delete c[map][key];
                          })
                        }
                      >
                        {t("মূল লেখা", "Restore")}
                      </button>
                    </div>
                  );
                })}
              </details>
            ))}
          </>
        ) : null}
        {pane === "seo" ? (
          <>
            <h2>
              {t("সার্চের শিরোনাম ও পরিচিতি", "Search titles and descriptions")}
            </h2>
            <CopyEditor
              label={t("শিরোনাম", "Title")}
              value={{ bn: draft.seo.title_bn, en: draft.seo.title_en }}
              onChange={(v) =>
                edit((c) => {
                  c.seo.title_bn = v.bn;
                  c.seo.title_en = v.en;
                })
              }
            />
            <CopyEditor
              label={t("বিবরণ", "Description")}
              value={{
                bn: draft.seo.description_bn,
                en: draft.seo.description_en,
              }}
              area
              onChange={(v) =>
                edit((c) => {
                  c.seo.description_bn = v.bn;
                  c.seo.description_en = v.en;
                })
              }
            />
            <label className="consent-row">
              <input
                type="checkbox"
                checked={draft.seo.index}
                onChange={(e) =>
                  edit((c) => {
                    c.seo.index = e.target.checked;
                  })
                }
              />
              {t(
                "সার্চ ইঞ্জিনকে public পাতা index করার অনুমতি দিন",
                "Allow search engines to index public pages",
              )}
            </label>
            <Notice>
              {t(
                "Indexing বন্ধ থাকাই ডিফল্ট। Private workspace ও admin পাতা সবসময় noindex থাকে।",
                "Indexing defaults to off. Private workspaces and admin pages always remain noindex.",
              )}
            </Notice>
          </>
        ) : null}
        {pane === "json" ? (
          <>
            <h2>
              {t("সম্পূর্ণ typed configuration", "Full typed configuration")}
            </h2>
            <label className="form-field">
              JSON
              <textarea
                className="site-json"
                spellCheck={false}
                rows={24}
                value={raw}
                onChange={(e) => setRaw(e.target.value)}
              />
            </label>
            <button
              disabled={busy}
              type="button"
              className="button outline"
              onClick={() =>
                action(
                  async () => {
                    const value = await api<{ config: SiteConfig }>(
                      "/api/admin/site-builder/validate",
                      {
                        method: "POST",
                        body: JSON.stringify({ config: JSON.parse(raw) }),
                      },
                    );
                    setDraft(value.config);
                  },
                  t(
                    "JSON যাচাই করে editor-এ নেওয়া হয়েছে; প্রকাশ হয়নি।",
                    "JSON validated and loaded into the editor; not published.",
                  ),
                )
              }
            >
              {t("যাচাই করে editor-এ নিন", "Validate & apply to editor")}
            </button>
          </>
        ) : null}
        {pane === "versions" ? (
          <>
            <h2>
              {t(
                "স্বাধীন পর্যালোচনা ও প্রকাশ",
                "Independent review and publication",
              )}
            </h2>
            <p>
              {t("বর্তমান সংস্করণ", "Current revision")}:{" "}
              <code>
                {state.active.revision || t("মূল নকশা", "Built-in design")}
              </code>
            </p>
            <label className="form-field">
              {t(
                "পর্যালোচনার কারণ (অন্তত ১০ অক্ষর)",
                "Review reason (at least 10 characters)",
              )}
              <textarea
                minLength={10}
                maxLength={1000}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </label>
            <label className="form-field">
              {t(
                "ভবিষ্যতের সময় (আপনার browser-এর স্থানীয় সময়)",
                "Future time (your browser’s local time)",
              )}
              <input
                type="datetime-local"
                value={due}
                onChange={(e) => setDue(e.target.value)}
              />
            </label>
            {state.versions.map((v) => (
              <article className="panel" key={v.id}>
                <div className="button-row">
                  <strong>{v.status}</strong>
                  <code>{v.id}</code>
                </div>
                <p>
                  {v.created_at} ·{" "}
                  {v.author === user?.id
                    ? t("আপনার লেখা", "Your draft")
                    : t("অন্য সম্পাদকের লেখা", "Another editor’s draft")}
                </p>
                <div className="button-row">
                  <button
                    type="button"
                    className="button outline small"
                    onClick={() => setPreview(v.id)}
                  >
                    {t("ব্যক্তিগত preview", "Private preview")}
                  </button>
                  <button
                    type="button"
                    disabled={busy}
                    className="button outline small"
                    onClick={() =>
                      action(
                        async () => {
                          const value = await api<{ config: SiteConfig }>(
                            `/api/admin/site-builder/${v.id}/preview`,
                          );
                          setDraft(structuredClone(value.config));
                          setDraftBaseRevision(state.active.revision);
                          setPane("brand");
                        },
                        t(
                          "সংস্করণটি editor-এ নেওয়া হয়েছে; প্রকাশ হয়নি।",
                          "Version copied to editor; not published.",
                        ),
                      )
                    }
                  >
                    {t("editor-এ নিন", "Copy to editor")}
                  </button>
                  {v.status === "draft" && v.author !== user?.id
                    ? (["approved", "rejected"] as const).map((decision) => (
                        <button
                          key={decision}
                          type="button"
                          disabled={busy || reason.trim().length < 10}
                          className="button outline small"
                          onClick={() =>
                            action(
                              async () => {
                                await api(
                                  `/api/admin/site-builder/${v.id}/review`,
                                  {
                                    method: "POST",
                                    body: JSON.stringify({ decision, reason }),
                                  },
                                );
                                await reload();
                              },
                              t("পর্যালোচনা রেকর্ড হয়েছে।", "Review recorded."),
                            )
                          }
                        >
                          {decision === "approved"
                            ? t("অনুমোদন", "Approve")
                            : t("প্রত্যাখ্যান", "Reject")}
                        </button>
                      ))
                    : null}
                  {v.status === "reviewed" ? (
                    <>
                      <button
                        type="button"
                        disabled={busy}
                        className="button dark small"
                        onClick={() =>
                          action(
                            async () => {
                              await api(
                                `/api/admin/site-builder/${v.id}/publish`,
                                {
                                  method: "POST",
                                  body: JSON.stringify({
                                    expected_revision: state.active.revision,
                                  }),
                                },
                              );
                              await reload();
                              await refreshSite();
                            },
                            t(
                              "পর্যালোচিত সংস্করণ প্রকাশ হয়েছে।",
                              "Reviewed version published.",
                            ),
                          )
                        }
                      >
                        {t("এখন প্রকাশ করুন", "Publish now")}
                      </button>
                      <button
                        type="button"
                        disabled={busy || !due}
                        className="button outline small"
                        onClick={() =>
                          action(
                            async () => {
                              await api("/api/admin/publishing", {
                                method: "POST",
                                body: JSON.stringify({
                                  version_id: v.id,
                                  due_at: Math.floor(
                                    new Date(due).getTime() / 1000,
                                  ),
                                }),
                              });
                              await reload();
                            },
                            t(
                              "সময়সূচি তৈরি হয়েছে; Publishing পাতায় অবস্থা দেখুন।",
                              "Scheduled; check the Publishing console for its outcome.",
                            ),
                          )
                        }
                      >
                        {t("সময় নির্ধারণ", "Schedule")}
                      </button>
                    </>
                  ) : null}
                  {v.status === "published" &&
                  v.id !== state.active.revision ? (
                    <button
                      type="button"
                      disabled={busy}
                      className="button outline small"
                      onClick={() =>
                        action(
                          async () => {
                            await api(
                              `/api/admin/site-builder/${v.id}/publish`,
                              {
                                method: "POST",
                                body: JSON.stringify({
                                  expected_revision: state.active.revision,
                                  rollback: true,
                                }),
                              },
                            );
                            await reload();
                            await refreshSite();
                          },
                          t(
                            "আগের পর্যালোচিত সংস্করণ ফিরেছে।",
                            "Earlier reviewed version restored.",
                          ),
                        )
                      }
                    >
                      {t("এই সংস্করণে ফিরে যান", "Roll back to this version")}
                    </button>
                  ) : null}
                </div>
              </article>
            ))}
            <Link href="/admin/publishing">
              {t(
                "সময়সূচি দেখুন বা বাতিল করুন",
                "Inspect or cancel publication schedules",
              )}{" "}
              →
            </Link>
          </>
        ) : null}
      </div>
      <div className="site-save-bar">
        <button
          disabled={busy}
          type="button"
          className="button outline"
          onClick={() =>
            action(
              async () => {
                await api("/api/admin/site-builder/validate", {
                  method: "POST",
                  body: JSON.stringify({ config: draft }),
                });
              },
              t(
                "সেটিংস বৈধ। এখন ড্রাফট সংরক্ষণ করতে পারবেন।",
                "Configuration is valid. You can now save a draft.",
              ),
            )
          }
        >
          {t("সেটিংস যাচাই", "Validate settings")}
        </button>
        <button
          disabled={busy}
          type="button"
          className="button dark"
          onClick={() =>
            action(
              async () => {
                const value = await api<{ id: string }>(
                  "/api/admin/site-builder",
                  {
                    method: "POST",
                    body: JSON.stringify({
                      config: draft,
                      expected_revision: draftBaseRevision,
                    }),
                  },
                );
                setPreview(value.id);
                await reload();
                setPane("versions");
              },
              t(
                "ব্যক্তিগত ড্রাফট সংরক্ষিত। আলাদা সম্পাদকের অনুমোদন প্রয়োজন।",
                "Private draft saved. Another editor must review it.",
              ),
            )
          }
        >
          {t("ড্রাফট সংরক্ষণ ও preview", "Save draft & preview")}
        </button>
        <button
          disabled={busy}
          type="button"
          className="button outline"
          onClick={() =>
            action(
              () => reload(true),
              t(
                "প্রকাশিত সেটিংস আবার নেওয়া হয়েছে।",
                "Published configuration reloaded.",
              ),
            )
          }
        >
          {t("প্রকাশিত সেটিংস ফিরিয়ে নিন", "Reload published settings")}
        </button>
      </div>
      {preview ? (
        <section className="site-preview-panel">
          <div className="section-heading">
            <h2>{t("ব্যক্তিগত ড্রাফট preview", "Private draft preview")}</h2>
            <button
              type="button"
              className="button outline small"
              onClick={() => setPreview("")}
            >
              {t("বন্ধ করুন", "Close")}
            </button>
          </div>
          <div className="button-row">
            {[390, 768, 1440].map((size) => (
              <button
                type="button"
                key={size}
                className="button outline small"
                aria-pressed={width === size}
                onClick={() => setWidth(size)}
              >
                {size}px
              </button>
            ))}
            <Link
              href={`/admin/site-preview/${preview}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {t("আলাদা tab-এ দেখুন", "Open in another tab")} ↗
            </Link>
          </div>
          <div className="site-preview-scroll">
            <iframe
              key={preview}
              src={`/admin/site-preview/${preview}`}
              title={t(
                "প্রকাশ না হওয়া সাইটের preview",
                "Unpublished site preview",
              )}
              style={{ width, height: 950 }}
            />
          </div>
          <p>
            {t(
              "এটি বাস্তব page-এর viewport preview। নতুন hosting বা AI inference চালানো হচ্ছে না।",
              "This is a viewport preview of the actual page. It does not provision hosting or trigger AI inference.",
            )}
          </p>
        </section>
      ) : null}
    </section>
  );
}

export function SitePreview({ version }: { version: string }) {
  const { api, user, loading, t, setPreviewSite } = useApp();
  const [ready, setReady] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    if (!user) return;
    let live = true;
    api<{ config: SiteConfig }>(
      `/api/admin/site-builder/${encodeURIComponent(version)}/preview`,
    )
      .then((v) => {
        if (live) {
          setPreviewSite(v.config);
          setReady(true);
        }
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
      setPreviewSite(null);
    };
  }, [api, user?.id, version, setPreviewSite, user]);
  if (error)
    return (
      <div className="page-width error" role="alert">
        {error}
        <p>
          <Link href="/admin/security">MFA</Link>
        </p>
      </div>
    );
  if (!loading && !user)
    return (
      <div className="page-width empty">
        <Link href="/admin/login">
          {t("প্রশাসনিক প্রবেশ প্রয়োজন", "Operator sign-in required")}
        </Link>
      </div>
    );
  if (!ready)
    return (
      <div className="page-width empty">
        {t("অনুমতি ও ড্রাফট যাচাই হচ্ছে…", "Checking permission and draft…")}
      </div>
    );
  return (
    <>
      <div className="site-draft-banner" role="status">
        {t("ব্যক্তিগত ড্রাফট · প্রকাশ হয়নি", "PRIVATE DRAFT · NOT PUBLISHED")} ·{" "}
        {version}
      </div>
      <Home />
    </>
  );
}
