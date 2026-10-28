"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "./context";
import { tools } from "./catalogue";
import { ResultView } from "./tool";
import { CollaborationPanel } from "./collaboration";
import type { RunResult, Workspace } from "./types";
type Row = { id: string; module: string; created_at: string; saved: boolean };
export function SessionWork({ pane = "history" }: { pane?: string }) {
  const { api, t, user, loading, refresh } = useApp();
  const [space, setSpace] = useState(""),
    [rows, setRows] = useState<Row[]>([]),
    [result, setResult] = useState<RunResult | null>(null),
    [error, setError] = useState(""),
    [confirm, setConfirm] = useState(false),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    if (!user) return;
    let live = true;
    api<Workspace[]>("/api/workspaces")
      .then(async (w) => {
        const id = w[0]?.id || "";
        const r = id
          ? await api<Row[]>("/api/workspaces/" + id + "/history")
          : [];
        if (live) {
          setSpace(id);
          setRows(r);
        }
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [api, user]);
  async function open(id: string) {
    try {
      const d = await api<{ id: string; output: RunResult }>("/api/runs/" + id);
      setResult({ ...d.output, id: d.id });
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <div className="page-width session-work">
      <div className="page-heading">
        <span className="eyebrow">
          {t("অ্যাকাউন্ট ছাড়াই কাজ", "WORK WITHOUT AN ACCOUNT")}
        </span>
        <h1>
          {t("এই browser session-এর কাজ", "Work in this browser session")}
        </h1>
        <p>
          {t(
            "নাম, ইমেইল বা profile লাগে না। এই browser-এর সুরক্ষিত session cookie-তে শুধু আপনার ফলাফল আলাদা থাকে। সাধারণ visitor session সর্বোচ্চ ২৪ ঘণ্টা থাকে; cookie হারালে কাজ ফেরত আনার অ্যাকাউন্ট নেই। প্রয়োজনীয় রিপোর্ট এখনই ডাউনলোড করুন।",
            "No name, email or profile is needed. A secure browser-session cookie keeps your results separate. Visitor sessions last up to 24 hours; there is no account recovery if the cookie is lost. Download reports you need to keep.",
          )}
        </p>
      </div>
      <nav className="tabs">
        <Link href="/work">{t("ফলাফল", "Results")}</Link>
        <Link href="/work/sharing">
          {t("সহায়তা ও transfer", "Support & transfers")}
        </Link>
        <Link href="/explore">{t("টুল খুলুন", "Open a tool")}</Link>
      </nav>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {loading ? (
        <p role="status">
          {t("Session প্রস্তুত হচ্ছে…", "Preparing session…")}
        </p>
      ) : !user ? (
        <p className="error">
          {t(
            "সেবা পাওয়া যাচ্ছে না। পৃষ্ঠা refresh করুন।",
            "Service unavailable. Refresh the page.",
          )}
        </p>
      ) : (
        <>
          {pane === "sharing" ? (
            <CollaborationPanel
              key={`${user.id}:${space}`}
              workspaceId={space}
              history={rows}
            />
          ) : (
            <>
              <section className="panel">
                <h2>{t("এই session-এর ফলাফল", "Session results")}</h2>
                {rows.length ? (
                  rows.map((r) => (
                    <article className="grant-card" key={r.id}>
                      <strong>
                        {tools.find((x) => x.slug === r.module)?.name}
                      </strong>
                      <div className="row-actions">
                        <button
                          className="text-link"
                          onClick={() => open(r.id)}
                        >
                          {t("দেখুন", "View")}
                        </button>
                        <a
                          className="text-link"
                          download
                          href={`/api/runs/${r.id}/export?format=pdf`}
                        >
                          {t("PDF ডাউনলোড", "Download PDF")}
                        </a>
                        <a
                          className="text-link"
                          download
                          href={`/api/runs/${r.id}/export?format=json`}
                        >
                          JSON
                        </a>
                      </div>
                    </article>
                  ))
                ) : (
                  <p>
                    {t(
                      "এখনো কোনো ফলাফল নেই। যেকোনো টুল সরাসরি খুলে কাজ করুন।",
                      "No results yet. Open any tool directly to start.",
                    )}
                  </p>
                )}
              </section>
              {result ? <ResultView result={result} /> : null}
              <section className="panel">
                <h2>
                  {t("নিজের তথ্যের নিয়ন্ত্রণ", "Control this session's data")}
                </h2>
                <a
                  className="button outline"
                  download
                  href="/api/privacy/export"
                >
                  {t("Session-এর তথ্য ডাউনলোড", "Download session data")}
                </a>
                {user.role === "guest" ? (
                  <>
                    <p>
                      {t(
                        "নিচের কাজটি শুধু বর্তমান session-এর ফলাফল ও ফাইল মুছবে।",
                        "This clears only this session's results and files.",
                      )}
                    </p>
                    <label className="consent-check">
                      <input
                        type="checkbox"
                        checked={confirm}
                        onChange={(e) => setConfirm(e.target.checked)}
                      />
                      <span>
                        {t(
                          "এই session-এর তথ্য মুছতে সম্মতি দিচ্ছি।",
                          "I confirm clearing this session's data.",
                        )}
                      </span>
                    </label>
                    <button
                      className="button outline danger"
                      disabled={!confirm || busy}
                      onClick={async () => {
                        setBusy(true);
                        try {
                          await api("/api/session/clear", {
                            method: "POST",
                            body: JSON.stringify({ confirm: true }),
                          });
                          setRows([]);
                          setResult(null);
                          setConfirm(false);
                          await refresh();
                        } catch (e) {
                          setError((e as Error).message);
                        } finally {
                          setBusy(false);
                        }
                      }}
                    >
                      {t("এই session মুছুন", "Clear this session")}
                    </button>
                  </>
                ) : null}
              </section>
            </>
          )}
        </>
      )}
    </div>
  );
}
