"use client";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { Fragment, type ReactNode, useState, useMemo, useEffect } from "react";
import {
  ArrowRight,
  Search,
  SlidersHorizontal,
  Leaf,
  HeartPulse,
  BookOpen,
  ShoppingBasket,
  Landmark,
  House,
  Activity,
  HandHeart,
  Store,
  ShieldCheck,
  AudioLines,
  FileText,
  Calculator,
} from "lucide-react";
import source from "@/packages/module-registry/catalogue.json";
import type { Tool } from "./types";
import { useApp } from "./context";
import { customizeTool } from "./site-config";
export const tools = source.modules as Tool[];
function useCatalogue() {
  const [items, setItems] = useState(tools);
  useEffect(() => {
    let live = true;
    fetch("/api/modules")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (live && d) setItems((d as { modules: Tool[] }).modules);
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, []);
  return items;
}

export const categories: Record<
  string,
  { bn: string; en: string; icon: typeof Leaf }
> = {
  agri: { bn: "কৃষি ও মৎস্য", en: "Agriculture & fisheries", icon: Leaf },
  climate: {
    bn: "পরিবেশ ও জলবায়ু",
    en: "Environment & climate",
    icon: Activity,
  },
  home: { bn: "ঘর ও আবাসন", en: "Housing & home", icon: House },
  civic: { bn: "নাগরিক ও অধিকার", en: "Civic & rights", icon: Landmark },
  consumer: {
    bn: "বাজার ও খরচ",
    en: "Shopping & expenses",
    icon: ShoppingBasket,
  },
  health: { bn: "স্বাস্থ্য সহায়তা", en: "Health support", icon: HeartPulse },
  sports: { bn: "খেলাধুলা", en: "Sports", icon: Activity },
  retail: { bn: "ছোট ব্যবসা", en: "Small business", icon: Store },
  education: { bn: "শেখা ও শিক্ষা", en: "Learning", icon: BookOpen },
  learning: { bn: "শেখা ও শিক্ষা", en: "Learning", icon: BookOpen },
  accessibility: { bn: "সহজ যোগাযোগ", en: "Accessibility", icon: HandHeart },
  safety: { bn: "নিরাপত্তা", en: "Safety", icon: ShieldCheck },
  digital: { bn: "ডিজিটাল নিরাপত্তা", en: "Digital safety", icon: ShieldCheck },
  transport: { bn: "যাতায়াত", en: "Transport", icon: Activity },
};
export function ToolCard({ tool: rawTool }: { tool: Tool }) {
  const { t, site, lang } = useApp();
  const tool = customizeTool(rawTool, site, lang);
  const c = site.category_labels[tool.category] || categories[tool.category];
  return (
    <Link
      href={"/tools/" + tool.slug}
      className={"tool-card category-" + tool.category}
    >
      <div className="tool-card-top">
        <Image unoptimized src={tool.logo} alt="" width="49" height="49" />
        <span
          className={
            "pill " + (tool.release_status === "blocked" ? "muted" : "")
          }
        >
          {tool.release_status === "blocked"
            ? t("নির্ভরতা বাকি", "Dependency pending")
            : t("সীমিত সহায়ক কাজ", "Limited support")}
        </span>
      </div>
      <p className="eyebrow">{c ? t(c.bn, c.en) : tool.category}</p>
      <h3>{tool.name}</h3>
      <p className="description">
        {t(tool.description_bn, tool.description_en)}
      </p>
      <div className="tool-card-footer">
        <span>{t("কাজের জায়গা খুলুন", "Open workspace")}</span>
        <ArrowRight size={18} />
      </div>
    </Link>
  );
}
export function Explore({ initialQuery = "" }: { initialQuery?: string }) {
  const { t, site, lang } = useApp();
  const rawCatalogue = useCatalogue();
  const catalogue = useMemo(
    () => rawCatalogue.map((x) => customizeTool(x, site, lang)),
    [rawCatalogue, site, lang],
  );
  const [query, setQuery] = useState(initialQuery),
    [category, setCategory] = useState("all");
  const cats = Array.from(new Set(catalogue.map((x) => x.category)));
  const filtered = useMemo(
    () =>
      catalogue.filter(
        (m) =>
          (category === "all" || m.category === category) &&
          [
            m.name,
            m.inputs,
            m.outputs,
            m.slug,
            m.description_en,
            m.description_bn,
            m.category,
          ]
            .join(" ")
            .toLocaleLowerCase()
            .includes(query.toLocaleLowerCase()),
      ),
    [query, category, catalogue],
  );
  return (
    <div className="page-width explore-page">
      <div className="page-heading">
        <span className="eyebrow">
          {t("সমাধানের সংগ্রহ", "THE TOOL COLLECTION")}
        </span>
        <h1>
          {t("আপনার কাজের টুলটি খুঁজুন।", "Find the right tool for your task.")}
        </h1>
        <p>
          {t(
            "৫০টি আলাদা কাজ, একটি পরিচিত কর্মক্ষেত্র। প্রতিটি টুলে বর্তমান সক্ষমতা দেখুন।",
            "50 distinct workflows, one familiar workspace. Check each tool’s current capabilities.",
          )}
        </p>
      </div>
      <div className="search-box catalogue-search">
        <Search size={21} />
        <input
          aria-label={t("টুল খুঁজুন", "Search tools")}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t(
            "নাম, সমস্যা বা কাজ লিখুন…",
            "Search by name, problem or task…",
          )}
        />
        <span>{filtered.length} / 50</span>
      </div>
      <div className="catalogue-layout">
        <aside className="category-list">
          <p className="eyebrow">
            <SlidersHorizontal size={14} />
            {t("কাজের ধরন", "FILTER BY TASK")}
          </p>
          <button
            aria-pressed={category === "all"}
            className={category === "all" ? "selected" : ""}
            onClick={() => setCategory("all")}
          >
            {t("সব টুল", "All tools")}
            <span>50</span>
          </button>
          {cats.map((key) => {
            const c = categories[key];
            const Icon = c?.icon || FileText;
            return (
              <button
                key={key}
                aria-pressed={category === key}
                className={category === key ? "selected" : ""}
                onClick={() => setCategory(key)}
              >
                <Icon size={17} />
                {site.category_labels[key]
                  ? t(
                      site.category_labels[key].bn,
                      site.category_labels[key].en,
                    )
                  : c
                    ? t(c.bn, c.en)
                    : key}
                <span>
                  {catalogue.filter((m) => m.category === key).length}
                </span>
              </button>
            );
          })}
          <div className="aside-note">
            <ShieldCheck size={25} />
            <strong>
              {t("আপনার তথ্য, আপনার নিয়ন্ত্রণ", "Your data, your control")}
            </strong>
            <p>
              {t(
                "কোনো অ্যাকাউন্ট ছাড়াই, আলাদা browser session-এ ফলাফল।",
                "No account needed. Results stay in your browser session.",
              )}
            </p>
          </div>
        </aside>
        <section aria-live="polite">
          <div className="results-label">
            <p>
              {t("দেখানো হচ্ছে", "Showing")} <strong>{filtered.length}</strong>{" "}
              {t("টি টুল", "tools")}
            </p>
            <span>
              {t(
                "স্বচ্ছ সক্ষমতা ও সীমাবদ্ধতা",
                "Transparent capability labels",
              )}
            </span>
          </div>
          <div className="tools-grid">
            {filtered.map((tool) => (
              <ToolCard key={tool.slug} tool={tool} />
            ))}
          </div>
          {!filtered.length ? (
            <div className="empty">
              <Search />
              <h3>{t("এই নামে টুল পাওয়া যায়নি", "No matching tools")}</h3>
              <p>
                {t(
                  "অন্য শব্দ বা কাজের ধরন বেছে নিন।",
                  "Try another word or category.",
                )}
              </p>
              <button
                className="button"
                onClick={() => {
                  setQuery("");
                  setCategory("all");
                }}
              >
                {t("সব টুল দেখুন", "Show all tools")}
              </button>
            </div>
          ) : null}
        </section>
      </div>
    </div>
  );
}
export function Home() {
  const catalogue = useCatalogue();
  const router = useRouter();
  const { t, site } = useApp();
  const copy = (key: string) =>
    t(site.home.text[key].bn, site.home.text[key].en);
  const [query, setQuery] = useState("");
  const highlights = site.home.featured_slugs
    .map((s) => catalogue.find((x) => x.slug === s))
    .filter(Boolean) as Tool[];
  const sections: Record<string, ReactNode> = {
    hero: (
      <section className="hero page-width">
        <div className="hero-content">
          <div className="hero-kicker">
            <span />
            {copy("hero_kicker")}
          </div>
          <h1>
            {copy("hero_title")}
            <br />
            <em>{copy("hero_accent")}</em>
          </h1>
          <p className="hero-intro">{copy("hero_intro")}</p>
          <form
            className="search-box hero-search"
            onSubmit={(e) => {
              e.preventDefault();
              router.push("/explore?q=" + encodeURIComponent(query));
            }}
          >
            <Search size={22} />
            <input
              aria-label={t("কী করতে চান?", "What would you like to do?")}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={copy("hero_search")}
            />
            <button className="icon-button" aria-label={t("খুঁজুন", "Search")}>
              <ArrowRight size={22} />
            </button>
          </form>
          <div className="try-links">
            <span>{t("যেমন:", "TRY:")}</span>
            {[
              [t("খরচের হিসাব", "expenses"), "bill"],
              [t("জমির মাপ", "land area"), "land"],
              [t("বাংলা শেখা", "learn Bengali"), "reading"],
            ].map(([name, q]) => (
              <Link key={q} href={"/explore?q=" + q}>
                {name} ↗
              </Link>
            ))}
          </div>
          <div className="hero-trust">
            <ShieldCheck size={17} />
            <span>{t("গোপনীয়তা আগে", "Privacy first")}</span>
            <span className="separator">/</span>
            <span>{t("উৎসসহ ফলাফল", "Evidence included")}</span>
            <span className="separator">/</span>
            <span>বাংলা + English</span>
          </div>
        </div>
        <div
          className="hero-art"
          aria-label={t("এক কেন্দ্র, নানা কাজ", "One hub, many tasks")}
        >
          <div className="art-grid" />
          <div className="art-caption">
            <span className="small-diamond" />
            {t(
              "একটা সংযোগ। অনেক সম্ভাবনা।",
              "ONE CONNECTION. MANY POSSIBILITIES.",
            )}
          </div>
          <div className="hub-core">
            <div className="hub-symbol">⬡</div>
            <strong>
              {t("মৌচাক", "Mouchak")}
              <span>AI</span>
            </strong>
          </div>
          <div className="orbit orbit-1">
            <BookOpen />
            <span>{t("শিখুন", "Learn")}</span>
          </div>
          <div className="orbit orbit-2">
            <Leaf />
            <span>{t("পরিচর্যা", "Care")}</span>
          </div>
          <div className="orbit orbit-3">
            <FileText />
            <span>{t("বুঝুন", "Understand")}</span>
          </div>
          <div className="orbit orbit-4">
            <Calculator />
            <span>{t("হিসাব করুন", "Calculate")}</span>
          </div>
          <div className="art-note">
            <span>50</span>
            <div>
              <strong>{t("ভিন্ন কাজের টুল", "PURPOSEFUL TOOLS")}</strong>
              <small>
                {t("এক কেন্দ্রীয় প্ল্যাটফর্মে", "ONE SHARED PLATFORM")}
              </small>
            </div>
            <ArrowUp />
          </div>
        </div>
      </section>
    ),
    statement: (
      <section className="statement-strip">
        <div className="page-width">
          <p>
            <strong>
              {t(
                "প্রযুক্তি বোঝার দরকার নেই।",
                "No technical expertise needed.",
              )}
            </strong>{" "}
            {t(
              "আপনার কাজটা জানলেই শুরু করা যায়।",
              "Just start with the task you need help with.",
            )}
          </p>
          <Link href="/methodology">
            {t("কীভাবে কাজ করে", "How it works")}
            <ArrowRight size={17} />
          </Link>
        </div>
      </section>
    ),
    featured: (
      <section className="page-width section-space">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              {t("শুরু করার কয়েকটি পথ", "A FEW PLACES TO START")}
            </span>
            <h2>{copy("featured_title")}</h2>
          </div>
          <Link className="text-link" href="/explore">
            {t("সব ৫০টি টুল দেখুন", "Explore all 50 tools")}
            <ArrowRight size={18} />
          </Link>
        </div>
        <div className="featured-grid">
          {highlights.map((m) => (
            <ToolCard key={m.slug} tool={m} />
          ))}
        </div>
      </section>
    ),
    principles: (
      <section className="page-width principles">
        <div>
          <span className="eyebrow">{t("আস্থার ভিত", "BUILT ON TRUST")}</span>
          <h2>
            {t("সহায়ক প্রযুক্তি।", "Helpful technology.")}
            <br />
            {t("সৎ সীমাবদ্ধতা।", "Honest limitations.")}
          </h2>
          <p>
            {t(
              "সব টুলের উন্নত AI প্রস্তুত নয়। কোন কাজ এখন চলে, কোন তথ্য যাচাই বাকি—আগেই জানবেন।",
              "Advanced AI is still being evaluated. See exactly what works today and what depends on further review.",
            )}
          </p>
          <Link className="text-link" href="/status">
            {t("সক্ষমতার বর্তমান অবস্থা", "See current readiness")}
            <ArrowRight size={18} />
          </Link>
        </div>
        <div className="principle-items">
          {[
            [
              ShieldCheck,
              t("ব্যক্তিগত মানেই ব্যক্তিগত", "Private means private"),
              t(
                "আপনার সংবেদনশীল নথি সাধারণ সার্চ বা অন্য ব্যবহারকারীর ফলাফলে যায় না।",
                "Sensitive records stay out of public search and other users’ results.",
              ),
            ],
            [
              FileText,
              t("উৎস দেখুন, নিজে যাচাই করুন", "Trace the evidence"),
              t(
                "আপনার দেওয়া তথ্য, নিজস্ব সহায়ক লেখা ও সরকারি রেফারেন্স আলাদা করে চিহ্নিত।",
                "Your inputs, project-authored passages and candidate official references are clearly labelled.",
              ),
            ],
            [
              AudioLines,
              t("আপনার মতো করে শুরু করুন", "Start your way"),
              t(
                "লিখে, সংখ্যা দিয়ে বা উপযুক্ত নথি দিয়ে। CSV আপলোড করা বাধ্যতামূলক নয়।",
                "Use text, numbers or supported documents. CSV uploads are never required.",
              ),
            ],
          ].map(([Icon, title, desc]) => {
            const I = Icon as typeof ShieldCheck;
            return (
              <article key={String(title)}>
                <I size={24} />
                <div>
                  <h3>{String(title)}</h3>
                  <p>{String(desc)}</p>
                </div>
              </article>
            );
          })}
        </div>
      </section>
    ),
    closing: (
      <section className="page-width closing">
        <div>
          <span className="eyebrow">
            {t("নিজের কাজের নিজস্ব জায়গা", "YOUR OWN SPACE")}
          </span>
          <h2>{copy("closing_title")}</h2>
          <p>
            {t(
              "কোনো login, signup বা profile নয়। সরাসরি কাজ করুন, ফলাফল ডাউনলোড করুন এবং session-এর তথ্য মুছুন।",
              "No login, signup or profile. Work directly, download reports and clear session data.",
            )}
          </p>
        </div>
        <Link className="button dark" href="/explore">
          {t("টুল বেছে নিন", "Choose a tool")}
          <ArrowRight size={18} />
        </Link>
      </section>
    ),
    faq: (
      <section id="faq" className="page-width section-space">
        <h2>{t("সাধারণ প্রশ্ন", "Frequently asked questions")}</h2>
        {site.home.faqs.map((faq, i) => (
          <details className="panel" key={i}>
            <summary>{t(faq.question.bn, faq.question.en)}</summary>
            <p>{t(faq.answer.bn, faq.answer.en)}</p>
          </details>
        ))}
      </section>
    ),
  };
  return (
    <>
      {site.home.sections.map((key) => (
        <Fragment key={key}>{sections[key]}</Fragment>
      ))}
    </>
  );
}
function ArrowUp() {
  return <ArrowRight size={28} className="rotate-up" />;
}
