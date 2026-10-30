"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "./context";
import { DataView } from "./tool";
type ModelState = {
  policy: { revision: string | null; state: string; reason: string };
  runtime: Record<string, unknown>;
  manifest: Record<string, unknown>;
};
type RoadState = {
  prepared: boolean;
  source_id?: string;
  source_state?: string;
  manifest?: Record<string, unknown>;
  detail?: string;
  active: { revision: string | null; source_id?: string };
};
export function PipelineOperations({
  tab,
}: {
  tab: "model-operations" | "road-data";
}) {
  const { api, t, user } = useApp();
  const [model, setModel] = useState<ModelState | null>(null),
    [road, setRoad] = useState<RoadState | null>(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [reason, setReason] = useState(""),
    [busy, setBusy] = useState(false);
  async function load() {
    if (tab === "model-operations")
      setModel(await api<ModelState>("/api/admin/model-operations"));
    else setRoad(await api<RoadState>("/api/admin/road-data"));
  }
  useEffect(() => {
    let live = true;
    api<ModelState | RoadState>("/api/admin/" + tab)
      .then((value) => {
        if (live) {
          if (tab === "model-operations") setModel(value as ModelState);
          else setRoad(value as RoadState);
        }
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [api, tab, user?.id]);
  async function action(work: () => Promise<unknown>, success: string) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await work();
      await load();
      setMessage(success);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="pipeline-operations">
      <div className="section-heading">
        <h1>
          {tab === "model-operations"
            ? t(
                "বাস্তব মডেলের অবস্থা ও নিয়ন্ত্রণ",
                "Actual model state and controls",
              )
            : t(
                "বাংলাদেশের public-road reference data",
                "Bangladesh public-road reference data",
              )}
        </h1>
        <Link href="/admin/security">MFA</Link>
      </div>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {message ? (
        <p className="success" role="status">
          {message}
        </p>
      ) : null}
      {model ? (
        <>
          <p className="notice">
            {t(
              "শুধু বাস্তব local experimental model disable/restore করা যায়। এই console দিয়ে production validation বা full-module completion দাবি চালু করা যায় না।",
              "Disable or restore the actual local experimental model. This console cannot enable production validation or full-module completion claims.",
            )}
          </p>
          <div className="panel">
            <DataView value={model.runtime} />
            <p>
              {t("বর্তমান নীতি", "Current policy")}:{" "}
              <strong>{model.policy.state}</strong>
            </p>
            <label className="form-field">
              {t("পরিবর্তনের কারণ", "Reason for change")}
              <textarea
                maxLength={1000}
                minLength={10}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </label>
            <div className="button-row">
              {(["disabled", "experimental"] as const).map((state) => (
                <button
                  key={state}
                  type="button"
                  disabled={
                    busy ||
                    reason.trim().length < 10 ||
                    state === model.policy.state
                  }
                  className="button outline"
                  onClick={() =>
                    action(
                      () =>
                        api("/api/admin/model-operations/noise-policy", {
                          method: "POST",
                          body: JSON.stringify({
                            state,
                            reason,
                            expected_revision: model.policy.revision,
                          }),
                        }),
                      t(
                        "নীতি বদল অডিটে সংরক্ষিত হয়েছে।",
                        "Policy change recorded in the audit.",
                      ),
                    )
                  }
                >
                  {state === "disabled"
                    ? t("Noise model বন্ধ করুন", "Disable noise model")
                    : t(
                        "Experimental gate ফিরিয়ে আনুন",
                        "Restore experimental gate",
                      )}
                </button>
              ))}
            </div>
            <details>
              <summary>
                {t(
                  "Checkpoint, hash, licence ও সীমাবদ্ধতা",
                  "Checkpoint, hashes, licence and limits",
                )}
              </summary>
              <DataView value={model.manifest} />
            </details>
          </div>
        </>
      ) : null}
      {road ? (
        <>
          <p className="notice">
            {t(
              "এটি নামযুক্ত সড়কের OSM reference index। গর্ত, দুর্ঘটনার ঝুঁকি, বর্তমান যানবাহন বা নিরাপদ পথের training label নেই। নামহীন পথ বাদ পড়ার সংখ্যা manifest-এ আছে।",
              "This is a named-road OSM reference index. It has no defect, crash-risk, live-traffic or safe-route training labels. The manifest reports omitted unnamed ways.",
            )}
          </p>
          <div className="panel">
            {road.prepared ? (
              <>
                <p>
                  {t("প্রস্তুত data", "Prepared data")}:{" "}
                  <code>{road.source_id}</code> · {road.source_state}
                </p>
                <DataView value={road.manifest} />
                <div className="button-row">
                  <button
                    type="button"
                    disabled={busy || road.source_state !== "not_registered"}
                    className="button outline"
                    onClick={() =>
                      action(
                        () =>
                          api("/api/admin/road-data/register", {
                            method: "POST",
                          }),
                        t(
                          "Candidate নিবন্ধিত হয়েছে; review ছাড়া প্রকাশ হয়নি।",
                          "Candidate registered; not published without review.",
                        ),
                      )
                    }
                  >
                    {t("Review-এর জন্য নিবন্ধন", "Register for review")}
                  </button>
                  <Link className="button outline" href="/admin/rights">
                    {t(
                      "দুই ভিন্ন reviewer-এর rights review",
                      "Rights review by two different reviewers",
                    )}
                  </Link>
                  <button
                    type="button"
                    disabled={
                      busy || road.source_state !== "approved_train_and_reuse"
                    }
                    className="button dark"
                    onClick={() =>
                      action(
                        () =>
                          api("/api/admin/road-data/publish", {
                            method: "POST",
                            body: JSON.stringify({
                              source_id: road.source_id,
                              expected_revision: road.active.revision,
                            }),
                          }),
                        t(
                          "পর্যালোচিত reference index প্রকাশ হয়েছে।",
                          "Reviewed reference index published.",
                        ),
                      )
                    }
                  >
                    {t("পর্যালোচিত index প্রকাশ", "Publish reviewed index")}
                  </button>
                  <button
                    type="button"
                    disabled={busy || !road.active.revision}
                    className="button outline"
                    onClick={() =>
                      action(
                        () =>
                          api("/api/admin/road-data/withdraw", {
                            method: "POST",
                            body: JSON.stringify({
                              expected_revision: road.active.revision,
                            }),
                          }),
                        t(
                          "Reference প্রত্যাহার হয়েছে।",
                          "Reference withdrawn.",
                        ),
                      )
                    }
                  >
                    {t("প্রত্যাহার করুন", "Withdraw")}
                  </button>
                </div>
                <p>
                  {t(
                    "একই source URL, ODbL licence ও public_nonpersonal sensitivity দিয়ে দুই ভিন্ন current reviewer অনুমোদন দেবেন। নিবন্ধনকারী নিজে প্রকাশ করতে পারবেন না।",
                    "Two different current reviewers must approve the same source URL, ODbL licence and public_nonpersonal sensitivity. The staging operator cannot publish their own index.",
                  )}
                </p>
              </>
            ) : (
              <>
                <p>{road.detail}</p>
                <p>
                  {t(
                    "Backend operator-কে documented prepare command চালাতে হবে। এটি কোনো cloud resource তৈরি করে না।",
                    "The backend operator must run the documented preparation command. It does not create cloud resources.",
                  )}
                </p>
                <code>uv pip install -r requirements-data.txt</code>
                <br />
                <code>python scripts/prepare-bd-roads.py --download</code>
              </>
            )}
            <p>
              {t("বর্তমান প্রকাশিত revision", "Current published revision")}:{" "}
              {road.active.revision || "—"}
            </p>
          </div>
        </>
      ) : null}
    </section>
  );
}
export function RoadReferenceLookup() {
  const { api, t, user, loading } = useApp();
  const [query, setQuery] = useState(""),
    [consent, setConsent] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [result, setResult] = useState<Record<string, unknown> | null>(null);
  return (
    <details className="panel road-reference">
      <summary>
        {t(
          "পর্যালোচিত public সড়কের নামের reference খুঁজুন",
          "Look up reviewed public road-name references",
        )}
      </summary>
      <p>
        {t(
          "এটি রাস্তার গর্ত বা নিরাপত্তা শনাক্ত করে না। আপনার query সংরক্ষণ করা হয় না।",
          "This does not detect road defects or safety. Your query is not stored.",
        )}
      </p>
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          setError("");
          try {
            setResult(
              await api("/api/tools/roadfix-bd/road-context", {
                method: "POST",
                body: JSON.stringify({ query, processing_consent: consent }),
              }),
            );
          } catch (error) {
            setError((error as Error).message);
            setResult(null);
          } finally {
            setBusy(false);
          }
        }}
      >
        <label className="form-field">
          {t("সড়কের নাম বা route reference", "Road name or route reference")}
          <input
            required
            minLength={2}
            maxLength={300}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <label className="consent-row">
          <input
            type="checkbox"
            required
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
          />
          {t(
            "শুধু এই reference খোঁজার জন্য query প্রক্রিয়াকরণে সম্মতি দিচ্ছি।",
            "I consent to processing this query only for this reference lookup.",
          )}
        </label>
        <button
          className="button outline"
          disabled={busy || loading || !user || !consent}
        >
          {busy
            ? t("খোঁজা হচ্ছে…", "Searching…")
            : t("Reference খুঁজুন", "Find references")}
        </button>
      </form>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {result ? (
        <div aria-live="polite">
          <DataView value={result} />
        </div>
      ) : null}
    </details>
  );
}
