"use client";
import { useEffect, useState } from "react";
import { useApp } from "./context";
import { DataView } from "./tool";
type Obj = Record<string, unknown>;
const codes: Record<string, [string, string]> = {
  new: ["নতুন", "New"],
  triaged: ["পর্যালোচিত", "Triaged"],
  in_progress: ["কাজ চলছে", "In progress"],
  resolved: ["সমাধান হয়েছে", "Resolved"],
  rejected: ["গৃহীত হয়নি", "Rejected"],
  bug: ["ত্রুটি", "Bug"],
  accessibility: ["অ্যাক্সেসিবিলিটি", "Accessibility"],
  content: ["কনটেন্ট", "Content"],
  privacy: ["গোপনীয়তা", "Privacy"],
  model_quality: ["মডেলের মান", "Model quality"],
  other: ["অন্যান্য", "Other"],
  approved_reference_only: ["শুধু তথ্যসূত্র হিসেবে অনুমোদিত", "Reference only"],
  approved_train_and_reuse: [
    "ট্রেনিং ও পুনর্ব্যবহারের অনুমোদন",
    "Training and reuse",
  ],
  revoked: ["বাতিল", "Revoked"],
  public_nonpersonal: ["প্রকাশ্য, ব্যক্তিগত নয়", "Public nonpersonal"],
  personal: ["ব্যক্তিগত", "Personal"],
  sensitive: ["সংবেদনশীল", "Sensitive"],
  scheduled: ["সময়সূচিতে আছে", "Scheduled"],
  published: ["প্রকাশিত", "Published"],
  cancelled: ["বাতিল", "Cancelled"],
  conflict: ["নতুন সংস্করণের সঙ্গে অমিল", "Version conflict"],
  rights_review: ["অনুমতি পর্যালোচনা চলছে", "Rights review"],
  candidate: ["প্রার্থী উৎস", "Candidate"],
  author_unavailable: ["লেখকের অনুমতি আর নেই", "Author no longer authorized"],
};
export function OperationsConsole({ tab }: { tab: string }) {
  const { api, t } = useApp();
  const code = (s: string) =>
    codes[s] ? t(...codes[s]) : s.replaceAll("_", " ");
  const [rows, setRows] = useState<Obj[]>([]),
    [versions, setVersions] = useState<Obj[]>([]),
    [recipients, setRecipients] = useState<Obj[]>([]),
    [selected, setSelected] = useState(""),
    [date, setDate] = useState(""),
    [view, setView] = useState<unknown>(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [form, setForm] = useState<Record<string, string>>({
      decision: "approved_train_and_reuse",
      sensitivity: "public_nonpersonal",
      status: "triaged",
      category: "bug",
    });
  const endpoint = tab === "rights" ? "sources" : tab;
  useEffect(() => {
    let live = true;
    api<Obj[]>("/api/admin/" + endpoint)
      .then((d) => {
        if (live) setRows(d);
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    if (tab === "notifications")
      api<Obj[]>("/api/admin/users")
        .then((d) => {
          if (live) setRecipients(d);
        })
        .catch((e) => {
          if (live) setError(e.message);
        });
    if (tab === "publishing")
      api<Obj[]>("/api/admin/cms")
        .then((d) => {
          if (live) setVersions(d);
        })
        .catch((e) => {
          if (live) setError(e.message);
        });
    return () => {
      live = false;
    };
  }, [api, tab, endpoint]);
  function set(k: string, v: string) {
    setForm({ ...form, [k]: v });
  }
  async function perform(fn: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    try {
      setView(await fn());
      setRows(await api<Obj[]>("/api/admin/" + endpoint));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="panel operations-console">
      {tab === "support" ? (
        <>
          <h2>
            {t("অনুমতি পাওয়া সহায়তার অনুরোধ", "Consented support requests")}
          </h2>
          <p>
            {t(
              "ব্যবহারকারী নির্দিষ্ট করে যে তথ্য দিয়েছেন, শুধু সেটি মেয়াদের মধ্যে দেখা যাবে। প্রতিবার দেখা অডিটে থাকবে।",
              "Only explicitly selected facts may be viewed before expiry. Every view is audited.",
            )}
          </p>
          {rows.map((r) => (
            <button
              key={String(r.id)}
              className="button outline small"
              disabled={busy}
              onClick={() => perform(() => api("/api/admin/support/" + r.id))}
            >
              {t("অনুমোদিত তথ্য দেখুন", "View permitted facts")} ·{" "}
              {String(r.id).slice(0, 8)}
            </button>
          ))}
        </>
      ) : null}
      {tab === "publishing" ? (
        <>
          <h2>{t("নির্ধারিত সময়ে প্রকাশ", "Scheduled publishing")}</h2>
          <p>
            {t(
              "এর মধ্যে পাতার প্রকাশিত লেখা বদলে গেলে পুরোনো schedule প্রকাশ হবে না; conflict দেখাবে। Scheduler worker চালু থাকা প্রয়োজন।",
              "A changed published page causes a schedule conflict instead of overwriting newer content. The scheduler worker must be running.",
            )}
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void perform(() =>
                api("/api/admin/publishing", {
                  method: "POST",
                  body: JSON.stringify({
                    version_id: selected,
                    due_at: Math.floor(new Date(date).getTime() / 1000),
                  }),
                }),
              );
            }}
          >
            <label className="form-field">
              {t("কনটেন্ট সংস্করণ", "Content version")}
              <select
                required
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
              >
                <option value="">{t("বাছুন", "Choose")}</option>
                {versions.map((v) => (
                  <option key={String(v.id)} value={String(v.id)}>
                    {String(v.page)} · {String(v.created_at)}
                  </option>
                ))}
              </select>
            </label>
            <label className="form-field">
              {t(
                "আপনার ডিভাইসের স্থানীয় তারিখ ও সময়",
                "Date and time in your device timezone",
              )}
              <input
                type="datetime-local"
                required
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </label>
            <button className="button dark" disabled={busy}>
              {t("সময় নির্ধারণ", "Schedule version")}
            </button>
          </form>
          {rows.map((r) => (
            <article className="grant-card" key={String(r.id)}>
              <strong>{String(r.page)}</strong>
              <p>
                {new Date(Number(r.due_at) * 1000).toLocaleString(undefined, {
                  timeZone: "Asia/Dhaka",
                })}{" "}
                (Asia/Dhaka) · {code(String(r.state))}
              </p>
              {r.state === "scheduled" ? (
                <button
                  className="button outline small"
                  disabled={busy}
                  onClick={() =>
                    perform(() =>
                      api(`/api/admin/publishing/${r.id}/cancel`, {
                        method: "POST",
                      }),
                    )
                  }
                >
                  {t("বাতিল", "Cancel")}
                </button>
              ) : null}
            </article>
          ))}
        </>
      ) : null}
      {tab === "feedback" ? (
        <>
          <h2>{t("মতামত পর্যালোচনা", "Feedback triage")}</h2>
          {rows.map((r) => (
            <article className="grant-card" key={String(r.id)}>
              <p>{String(r.text)}</p>
              <p>
                {code(String(r.status))} · {code(String(r.category))}
              </p>
              <select
                aria-label={t("অবস্থা", "Status")}
                value={code(String(r.status))}
                onChange={(e) =>
                  perform(() =>
                    api(`/api/admin/feedback/${r.id}`, {
                      method: "PATCH",
                      body: JSON.stringify({
                        status: e.target.value,
                        category: String(r.category),
                      }),
                    }),
                  )
                }
              >
                {["new", "triaged", "in_progress", "resolved", "rejected"].map(
                  (x) => (
                    <option key={x} value={x}>
                      {code(x)}
                    </option>
                  ),
                )}
              </select>
              <select
                aria-label={t("ধরন", "Category")}
                value={code(String(r.category))}
                onChange={(e) =>
                  perform(() =>
                    api(`/api/admin/feedback/${r.id}`, {
                      method: "PATCH",
                      body: JSON.stringify({
                        status: String(r.status),
                        category: e.target.value,
                      }),
                    }),
                  )
                }
              >
                {[
                  "bug",
                  "accessibility",
                  "content",
                  "privacy",
                  "model_quality",
                  "other",
                ].map((x) => (
                  <option key={x} value={x}>
                    {code(x)}
                  </option>
                ))}
              </select>
            </article>
          ))}
        </>
      ) : null}
      {tab === "notifications" ? (
        <>
          <h2>{t("ব্যক্তিগত সেবার নোটিশ", "Private service notice")}</h2>
          <p>
            {t(
              "একজন নির্দিষ্ট ব্যবহারকারীর অ্যাকাউন্টে বাংলা ও ইংরেজি নোটিশ যাবে। ইমেইল বা প্রচারাভিযান পাঠানো হবে না।",
              "Create a bilingual in-app notice for one selected account. This does not send email or a marketing campaign.",
            )}
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void perform(() =>
                api("/api/admin/notifications", {
                  method: "POST",
                  body: JSON.stringify({
                    user_id: selected,
                    body_bn: form.body_bn || "",
                    body_en: form.body_en || "",
                  }),
                }),
              );
            }}
          >
            <label className="form-field">
              {t("প্রাপক", "Recipient")}
              <select
                required
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
              >
                <option value="">{t("বাছুন", "Choose")}</option>
                {recipients.map((u) => (
                  <option key={String(u.id)} value={String(u.id)}>
                    {String(u.name)} · {String(u.email)}
                  </option>
                ))}
              </select>
            </label>
            {["bn", "en"].map((l) => (
              <label className="form-field" key={l}>
                {l === "bn" ? "বাংলা নোটিশ" : "English notice"}
                <textarea
                  required
                  maxLength={1000}
                  value={form["body_" + l] || ""}
                  onChange={(e) => set("body_" + l, e.target.value)}
                />
              </label>
            ))}
            <button className="button dark" disabled={busy}>
              {t("এই অ্যাকাউন্টে নোটিশ দিন", "Create notice for this account")}
            </button>
          </form>
          <h3>{t("আপনার তৈরি নোটিশের রেকর্ড", "Your dispatch records")}</h3>
          <DataView value={rows} />
        </>
      ) : null}
      {tab === "rights" ? (
        <>
          <h2>
            {t(
              "নির্দিষ্ট asset-এর স্বাধীন অনুমতি পর্যালোচনা",
              "Independent asset rights reviews",
            )}
          </h2>
          <p>
            {t(
              "সংবেদনশীল ডেটা training/reuse-এর জন্য একই asset ও scope-এ দুইজন আলাদা অনুমোদিত reviewer লাগবে। এটি নিজে থেকে ডেটা import করে না।",
              "Sensitive training/reuse needs two distinct authorized reviewers agreeing on the same asset and scope. Approval does not import data.",
            )}
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void perform(() =>
                api(`/api/admin/sources/${selected}/reviews`, {
                  method: "POST",
                  body: JSON.stringify(form),
                }),
              );
            }}
          >
            <label className="form-field">
              {t("উৎস", "Source")}
              <select
                value={selected}
                required
                onChange={(e) => {
                  setSelected(e.target.value);
                  setView(null);
                }}
              >
                <option value="">{t("বাছুন", "Choose")}</option>
                {rows.map((r) => (
                  <option key={String(r.id)} value={String(r.id)}>
                    {String(r.id)} · {String(r.module)} ·{" "}
                    {code(String(r.state))}
                  </option>
                ))}
              </select>
            </label>
            {[
              "asset_url",
              "terms_url",
              "license_uri",
              "scope",
              "coverage",
              "source_date",
              "evidence",
            ].map((k, i) => (
              <label className="form-field" key={k}>
                {
                  [
                    t("নির্দিষ্ট ফাইলের URL", "Exact asset URL"),
                    t("শর্তাবলির URL", "Terms URL"),
                    t("লাইসেন্স URL", "License URL"),
                    t("কী কাজে ব্যবহার অনুমোদিত", "Permitted use scope"),
                    t("ভৌগোলিক পরিধি", "Geographic coverage"),
                    t("উৎসের তারিখ", "Source date"),
                    t(
                      "অনুমতির প্রমাণ ও পর্যালোচনা",
                      "Rights evidence and review",
                    ),
                  ][i]
                }
                <input
                  type={
                    k.endsWith("url") || k === "license_uri"
                      ? "url"
                      : k === "source_date"
                        ? "date"
                        : "text"
                  }
                  required
                  maxLength={k === "evidence" ? 4000 : 2000}
                  value={form[k] || ""}
                  onChange={(e) => set(k, e.target.value)}
                />
              </label>
            ))}
            <label className="form-field">
              {t("সিদ্ধান্ত", "Decision")}
              <select
                value={form.decision}
                onChange={(e) => set("decision", e.target.value)}
              >
                {[
                  "approved_reference_only",
                  "approved_train_and_reuse",
                  "revoked",
                ].map((x) => (
                  <option key={x} value={x}>
                    {code(x)}
                  </option>
                ))}
              </select>
            </label>
            <label className="form-field">
              {t("সংবেদনশীলতা", "Sensitivity")}
              <select
                value={form.sensitivity}
                onChange={(e) => set("sensitivity", e.target.value)}
              >
                {["public_nonpersonal", "personal", "sensitive"].map((x) => (
                  <option key={x} value={x}>
                    {code(x)}
                  </option>
                ))}
              </select>
            </label>
            <button className="button dark" disabled={busy}>
              {t("নিজের পর্যালোচনা রেকর্ড করুন", "Record my review")}
            </button>
          </form>
          <button
            className="button outline"
            disabled={!selected || busy}
            onClick={() =>
              perform(() => api(`/api/admin/sources/${selected}/reviews`))
            }
          >
            {t("আগের review দেখুন", "View review history")}
          </button>
        </>
      ) : null}
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {view ? (
        <div aria-live="polite">
          <DataView value={view} />
        </div>
      ) : null}
    </div>
  );
}
