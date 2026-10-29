"use client";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "./context";
import { DataView } from "./tool";

type DirectoryState = {
  active: Record<string, string | null>;
  batches: {
    id: string;
    module: string;
    state: string;
    records: number;
    owner: string;
  }[];
};
type Source = { id: string; module: string; state: string };

export function DirectoryConsole() {
  const { api, t, user } = useApp();
  const [data, setData] = useState<DirectoryState | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [source, setSource] = useState("");
  const [raw, setRaw] = useState("");
  const [preview, setPreview] = useState<unknown>(null);
  const [reviewedId, setReviewedId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const load = useCallback(async () => {
    const [state, candidates] = await Promise.all([
      api<DirectoryState>("/api/admin/directories"),
      api<Source[]>("/api/admin/sources"),
    ]);
    setData(state);
    setSources(
      candidates.filter(
        (s) =>
          ["cliniccompass-bd", "oshudhkhoj-bd"].includes(s.module) &&
          s.state === "approved_train_and_reuse",
      ),
    );
  }, [api]);
  useEffect(() => {
    let active = true;
    Promise.all([
      api<DirectoryState>("/api/admin/directories"),
      api<Source[]>("/api/admin/sources"),
    ])
      .then(([state, candidates]) => {
        if (!active) return;
        setData(state);
        setSources(
          candidates.filter(
            (s) =>
              ["cliniccompass-bd", "oshudhkhoj-bd"].includes(s.module) &&
              s.state === "approved_train_and_reuse",
          ),
        );
      })
      .catch((e: Error) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [api]);
  async function action(work: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await work();
      await load();
      setNotice(
        t(
          "পরিবর্তন সংরক্ষিত ও অডিটে রেকর্ড হয়েছে।",
          "Saved and recorded in the audit log.",
        ),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const selected = sources.find((s) => s.id === source);
  return (
    <>
      <h1>{t("অনুমোদিত সেবার তালিকা", "Reviewed service directories")}</h1>
      <p>
        {t(
          "হাসপাতাল বা ফার্মেসির প্রকাশযোগ্য, অনুমতিপ্রাপ্ত তালিকা। রোগী বা ব্যক্তিগত রেকর্ড দেবেন না।",
          "Publishable, rights-cleared facility or pharmacy directories. Do not submit patient or personal records.",
        )}
      </p>
      <p>
        <Link href="/admin/rights">
          {t("উৎসের দুই স্বাধীন পর্যালোচনা", "Two independent asset reviews")}
        </Link>
      </p>
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
      {notice && (
        <p className="success-message" role="status">
          {notice}
        </p>
      )}
      <section className="panel">
        <h2>{t("প্রকাশের আগে যাচাই", "Validate before publishing")}</h2>
        <p>
          {t(
            "কেন্দ্রের তথ্য ৯০ দিনের মধ্যে, ওষুধের তথ্য ২৪ ঘণ্টার মধ্যে যাচাই করা হতে হবে। অন্য প্রশাসক ব্যাচটি প্রকাশ করবেন।",
            "Facility records must be verified within 90 days; pharmacy records within 24 hours. A different operator must publish the batch.",
          )}
        </p>
        <label className="form-field">
          {t("অনুমোদিত উৎস", "Approved source")}
          <select
            value={source}
            onChange={(e) => {
              setSource(e.target.value);
              setPreview(null);
              setReviewedId("");
            }}
          >
            <option value="">
              {t("উৎস নির্বাচন করুন", "Select a source")}
            </option>
            {sources.map((s) => (
              <option key={s.id} value={s.id}>
                {s.id} · {s.module}
              </option>
            ))}
          </select>
        </label>
        {!sources.length && (
          <p>
            {t(
              "এখন কোনো অনুমোদিত উৎস নেই। আগে rights review সম্পন্ন করুন।",
              "No approved sources are available. Complete asset rights review first.",
            )}
          </p>
        )}
        <label className="form-field">
          {t(
            "JSON রেকর্ডের তালিকা (সর্বোচ্চ ২০০)",
            "JSON record array (up to 200)",
          )}
          <textarea
            rows={12}
            className="code-editor"
            value={raw}
            onChange={(e) => {
              setRaw(e.target.value);
              setPreview(null);
              setReviewedId("");
            }}
          />
        </label>
        <p>
          {t(
            "ফিল্ড ও স্কিমা: repository-এর docs/DIRECTORY_PIPELINE.md। কোনো নমুনা রেকর্ড স্বয়ংক্রিয়ভাবে প্রকাশ করা হয় না।",
            "Fields and schemas: docs/DIRECTORY_PIPELINE.md in the repository. No sample records are automatically published.",
          )}
        </p>
        <button
          className="button dark"
          disabled={busy || !selected || !raw.trim()}
          onClick={() =>
            action(async () => {
              setReviewedId("");
              setPreview(
                await api("/api/admin/directories/dry-run", {
                  method: "POST",
                  body: JSON.stringify({
                    source_id: source,
                    schema_name:
                      selected?.module === "cliniccompass-bd"
                        ? "facility_v1"
                        : "pharmacy_v1",
                    records: JSON.parse(raw),
                  }),
                }),
              );
            })
          }
        >
          {t("যাচাই ও প্রিভিউ", "Validate & preview")}
        </button>
        {!reviewedId && preview !== null ? <DataView value={preview} /> : null}
      </section>
      <section className="panel">
        <h2>{t("সক্রিয় সংস্করণ", "Active revisions")}</h2>
        {data &&
          Object.entries(data.active).map(([slug, revision]) => (
            <div className="cms-version" key={slug}>
              <div>
                <strong>{slug}</strong>
                <p>
                  {revision ||
                    t("প্রকাশিত তালিকা নেই", "No published directory")}
                </p>
              </div>
              <button
                className="button outline small"
                disabled={busy || !revision}
                onClick={() =>
                  action(() =>
                    api(`/api/admin/directories/${slug}/withdraw`, {
                      method: "POST",
                      body: JSON.stringify({ expected_revision: revision }),
                    }),
                  )
                }
              >
                {t("প্রত্যাহার", "Withdraw")}
              </button>
            </div>
          ))}
      </section>
      <section className="panel">
        <h2>{t("পর্যালোচনার ব্যাচ", "Review batches")}</h2>
        <button
          className="button outline small"
          disabled={busy}
          onClick={() => action(load)}
        >
          {t("তালিকা রিফ্রেশ", "Refresh list")}
        </button>
        {data?.batches.map((batch) => (
          <article className="cms-version" key={batch.id}>
            <div>
              <strong>{batch.module}</strong>
              <p>
                {batch.id} · {batch.records} · {batch.state}
              </p>
              {batch.owner === user?.id && (
                <small>
                  {t(
                    "আপনার ব্যাচ—অন্য প্রশাসক প্রকাশ করবেন।",
                    "Your batch needs another operator's publication decision.",
                  )}
                </small>
              )}
            </div>
            <button
              className="button outline small"
              disabled={busy}
              onClick={() =>
                action(async () => {
                  setPreview(await api(`/api/admin/directories/${batch.id}`));
                  setReviewedId(batch.id);
                })
              }
            >
              {t("সম্পূর্ণ ব্যাচ পর্যালোচনা", "Review complete batch")}
            </button>
            <button
              className="button outline small"
              disabled={
                busy ||
                reviewedId !== batch.id ||
                batch.owner === user?.id ||
                !["directory_dry_run", "directory_retired"].includes(
                  batch.state,
                )
              }
              onClick={() =>
                action(() =>
                  api(`/api/admin/directories/${batch.id}/publish`, {
                    method: "POST",
                    body: JSON.stringify({
                      expected_revision: data.active[batch.module] || null,
                    }),
                  }),
                )
              }
            >
              {t("এই সংস্করণ প্রকাশ", "Publish this revision")}
            </button>
          </article>
        ))}
      </section>
      {reviewedId && preview !== null ? (
        <section className="panel">
          <h2>
            {t("পর্যালোচনার সম্পূর্ণ রেকর্ড", "Complete records for review")}
          </h2>
          <DataView value={preview} />
        </section>
      ) : null}
    </>
  );
}
