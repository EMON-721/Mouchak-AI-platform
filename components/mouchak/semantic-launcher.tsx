"use client";
import { useRef, useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "./context";
import type { Tool } from "./types";
import { customizeTool } from "./site-config";
type Suggestion = {
  slug: string;
  name: string;
  route: string;
  why_bn: string;
  why_en: string;
  release_status: string;
  similarity_not_probability: number;
};
type Reply = {
  supported: boolean;
  state: string;
  suggestions: Suggestion[];
  message_bn: string;
  message_en: string;
  model_version?: string;
  model_inference_performed: boolean;
  query_stored: boolean;
};
export function SemanticLauncher({
  query,
  catalogue,
}: {
  query: string;
  catalogue: Tool[];
}) {
  const { api, t, lang, user, loading, site } = useApp();
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [answer, setAnswer] = useState<{ query: string; reply: Reply } | null>(
      null,
    );
  const abort = useRef<AbortController | null>(null);
  useEffect(() => () => abort.current?.abort(), []);
  async function run() {
    if (busy) return;
    setError("");
    setBusy(true);
    const controller = new AbortController();
    abort.current = controller;
    try {
      const reply = await api<Reply>("/api/launcher", {
        method: "POST",
        signal: controller.signal,
        body: JSON.stringify({ query, language: lang }),
      });
      setAnswer({ query, reply });
    } catch (e) {
      if ((e as Error).name !== "AbortError") setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const reply = answer?.query === query ? answer.reply : null;
  return (
    <section
      className="semantic-launcher panel"
      aria-label={t("কাজ অনুযায়ী টুল বাছাই", "Find a tool by task")}
    >
      <div className="section-heading">
        <div>
          <h2>
            {t(
              "নাম জানেন না? কাজটা লিখুন।",
              "Not sure of the name? Describe your task.",
            )}
          </h2>
          <p>
            {t(
              "উপরের search box-এর বর্ণনা দিয়ে multilingual model চালান। প্রশ্ন সংরক্ষণ বা অন্য টুলে পাঠানো হয় না।",
              "Use the description in the search box with the multilingual model. Your query is not stored or sent to another tool.",
            )}
          </p>
        </div>
        <button
          type="button"
          className="button outline"
          disabled={
            busy ||
            loading ||
            !user ||
            query.trim().length < 3 ||
            query.length > 800
          }
          onClick={run}
        >
          {busy
            ? t("টুল মিলিয়ে দেখা হচ্ছে…", "Matching tasks…")
            : t("বর্ণনা দিয়ে টুল খুঁজুন", "Match my task")}
        </button>
      </div>
      {query.length > 800 ? (
        <p>
          {t(
            "বর্ণনা ৮০০ অক্ষরের মধ্যে রাখুন।",
            "Keep the description within 800 characters.",
          )}
        </p>
      ) : null}
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {reply ? (
        <div aria-live="polite">
          <p className={reply.state === "urgent_help" ? "notice" : "subtle"}>
            {t(reply.message_bn, reply.message_en)}
          </p>
          <div className="semantic-options">
            {reply.suggestions.map((s) => {
              const original = catalogue.find((x) => x.slug === s.slug);
              const tool = original
                ? customizeTool(original, site, lang)
                : null;
              return (
                <Link className="semantic-option" key={s.slug} href={s.route}>
                  <strong>{tool?.name || s.name}</strong>
                  <p>
                    {tool
                      ? t(tool.description_bn, tool.description_en)
                      : t(s.why_bn, s.why_en)}
                  </p>
                  <span>
                    {s.release_status === "blocked"
                      ? t(
                          "প্রয়োজনীয় data/model এখনও বাকি",
                          "Required data/model is pending",
                        )
                      : t(
                          "বর্তমান সক্ষমতা দেখে খুলুন",
                          "Review current capabilities",
                        )}{" "}
                    →
                  </span>
                </Link>
              );
            })}
          </div>
          {reply.model_inference_performed ? (
            <small>
              {t(
                "এটি টুল বাছাইয়ের সহায়তা; similarity কোনো নিশ্চিত সম্ভাবনা বা চিকিৎসা সিদ্ধান্ত নয়।",
                "This assists tool selection; similarity is not a calibrated probability or medical decision.",
              )}{" "}
              · {reply.model_version}
            </small>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
