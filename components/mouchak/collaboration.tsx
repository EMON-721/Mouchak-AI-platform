"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "./context";
import { DataView } from "./tool";
import { tools } from "./catalogue";
import rawFields from "@/packages/module-registry/fields.json";
type Obj = Record<string, unknown>;
type Field = { key: string; type: string; bn: string; en: string };
const fieldRegistry = rawFields as Record<string, Field[]>;
type Grant = {
  id: string;
  recipient_email: string;
  reason: string;
  fact_keys: string[];
  expires_at: number;
  active: boolean;
};
type Draft = {
  id: string;
  target_module: string;
  workspace_id: string;
  state: string;
};
type Source = {
  id: string;
  module: string;
  inputs: Obj;
  output: { facts: Obj };
};
export function CollaborationPanel({
  workspaceId,
  history,
}: {
  workspaceId: string;
  history: { id: string; module: string; created_at: string }[];
}) {
  const { api, t, lang } = useApp();
  const [sourceId, setSourceId] = useState(""),
    [source, setSource] = useState<Source | null>(null),
    [grants, setGrants] = useState<Grant[]>([]),
    [drafts, setDrafts] = useState<Draft[]>([]),
    [email, setEmail] = useState(""),
    [reason, setReason] = useState(""),
    [minutes, setMinutes] = useState("15"),
    [facts, setFacts] = useState<string[]>([]),
    [supportConsent, setSupportConsent] = useState(false),
    [transferConsent, setTransferConsent] = useState(false),
    [target, setTarget] = useState(""),
    [mapping, setMapping] = useState<Record<string, string>>({}),
    [preview, setPreview] = useState<unknown>(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    let live = true;
    Promise.all([
      api<Grant[]>("/api/support/grants"),
      api<Draft[]>("/api/transfers"),
    ])
      .then(([g, d]) => {
        if (live) {
          setGrants(g);
          setDrafts(d);
        }
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [api]);
  useEffect(() => {
    if (!sourceId) return;
    let live = true;
    api<Source>("/api/runs/" + sourceId)
      .then((s) => {
        if (live) setSource(s);
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [sourceId, api]);
  const sourceTool = tools.find((x) => x.slug === source?.module),
    targetTool = tools.find((x) => x.slug === target);
  const sourceFields = (
    sourceTool ? fieldRegistry[sourceTool.engine] : []
  ).filter((f) => source && Object.hasOwn(source.inputs, f.key));
  const targetFields = targetTool ? fieldRegistry[targetTool.engine] : [];
  const payload = {
    source_run_id: sourceId,
    target_module: target,
    workspace_id: workspaceId,
    mapping: Object.entries(mapping)
      .filter(([, v]) => v)
      .map(([source, target]) => ({ source, target })),
    consent: transferConsent,
  };
  async function perform(fn: () => Promise<void>) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await fn();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="collaboration-stack">
      <section className="panel">
        <h2>{t("কোন ফলাফল নিয়ে কাজ করবেন?", "Choose a result")}</h2>
        <label className="form-field">
          {t("নিজের ফলাফল", "Your result")}
          <select
            value={sourceId}
            onChange={(e) => {
              setSourceId(e.target.value);
              setSource(null);
              setFacts([]);
              setMapping({});
              setPreview(null);
              setSupportConsent(false);
              setTransferConsent(false);
            }}
          >
            <option value="">{t("বাছুন", "Choose")}</option>
            {history.map((r) => (
              <option value={r.id} key={r.id}>
                {tools.find((x) => x.slug === r.module)?.name} ·{" "}
                {new Date(r.created_at).toLocaleDateString(
                  lang === "bn" ? "bn-BD" : "en-GB",
                  { timeZone: "Asia/Dhaka" },
                )}
              </option>
            ))}
          </select>
        </label>
        <p>
          {t(
            "কোন তথ্য যাবে, কাকে যাবে এবং কতক্ষণ থাকবে—সব আপনি বাছবেন।",
            "Choose exactly what to share, who receives it and for how long.",
          )}
        </p>
      </section>
      {source ? (
        <>
          <section className="panel">
            <h2>{t("সীমিত সময়ের সহায়তা", "Temporary support access")}</h2>
            <p>
              {t(
                "শুধু বাছা ফলাফলের তথ্য দেখা যাবে। মূল ইনপুট, ছবি বা নথির অনুমতি দেওয়া হবে না। মেয়াদ সর্বোচ্চ ৬০ মিনিট; যেকোনো সময় বাতিল করুন।",
                "Only selected result facts are shared. Inputs and original files remain private. Access lasts up to 60 minutes and can be revoked at any time.",
              )}
            </p>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void perform(async () => {
                  const g = await api<Grant>("/api/support/grants", {
                    method: "POST",
                    body: JSON.stringify({
                      run_id: sourceId,
                      recipient_email: email,
                      reason,
                      minutes: Number(minutes),
                      fact_keys: facts,
                      consent: supportConsent,
                    }),
                  });
                  setGrants([g, ...grants]);
                  setSupportConsent(false);
                  setMessage(
                    t("সীমিত অনুমতি দেওয়া হয়েছে।", "Temporary access granted."),
                  );
                });
              }}
            >
              <label className="form-field">
                {t(
                  "অনুমোদিত সহায়তাকারীর ইমেইল",
                  "Authorized support agent email",
                )}
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </label>
              <label className="form-field">
                {t("সহায়তার কারণ", "Reason for support")}
                <textarea
                  required
                  minLength={10}
                  maxLength={1000}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                />
              </label>
              <label className="form-field">
                {t("মেয়াদ (মিনিট)", "Duration (minutes)")}
                <input
                  type="number"
                  min={1}
                  max={60}
                  required
                  value={minutes}
                  onChange={(e) => setMinutes(e.target.value)}
                />
              </label>
              <fieldset>
                <legend>
                  {t("ঠিক কোন তথ্য দেখাবেন?", "Which facts may be viewed?")}
                </legend>
                {Object.entries(source.output.facts).map(([key, value]) => (
                  <label className="consent-check" key={key}>
                    <input
                      type="checkbox"
                      checked={facts.includes(key)}
                      onChange={(e) =>
                        setFacts(
                          e.target.checked
                            ? [...facts, key]
                            : facts.filter((k) => k !== key),
                        )
                      }
                    />
                    <span>
                      {key.replaceAll("_", " ")}: <DataView value={value} />
                    </span>
                  </label>
                ))}
              </fieldset>
              <label className="consent-check">
                <input
                  type="checkbox"
                  checked={supportConsent}
                  onChange={(e) => setSupportConsent(e.target.checked)}
                />
                <span>
                  {t(
                    "এই ব্যক্তিকে শুধু বাছা তথ্য নির্ধারিত সময়ের জন্য দেখানোর অনুমতি দিচ্ছি।",
                    "I permit this recipient to view only these selected facts for the chosen duration.",
                  )}
                </span>
              </label>
              <button
                className="button dark"
                disabled={busy || !supportConsent || !facts.length}
              >
                {t("সীমিত অনুমতি দিন", "Grant temporary access")}
              </button>
            </form>
          </section>
          <section className="panel">
            <h2>
              {t("অন্য টুলে বাছা তথ্য নিন", "Prepare a draft for another tool")}
            </h2>
            <p>
              {t(
                "তথ্য স্বয়ংক্রিয়ভাবে বিশ্লেষণ হবে না। গন্তব্য টুলে গিয়ে তথ্য ও একক দেখে সম্মতি দিয়ে চালাতে হবে।",
                "A transfer does not run analysis. Review the values and units in the destination tool, then separately consent to processing.",
              )}
            </p>
            <label className="form-field">
              {t("গন্তব্য টুল", "Destination tool")}
              <select
                value={target}
                onChange={(e) => {
                  setTarget(e.target.value);
                  setMapping({});
                  setPreview(null);
                  setTransferConsent(false);
                }}
              >
                <option value="">{t("বাছুন", "Choose")}</option>
                {tools
                  .filter((x) => x.slug !== source.module)
                  .map((x) => (
                    <option
                      value={x.slug}
                      key={x.slug}
                      disabled={x.release_status === "blocked"}
                    >
                      {x.name}
                      {x.release_status === "blocked"
                        ? t(" · চালু নেই", " · unavailable")
                        : ""}
                    </option>
                  ))}
              </select>
            </label>
            {sourceFields.map((f) => (
              <label className="form-field" key={f.key}>
                {lang === "bn" ? f.bn : f.en} →{" "}
                <select
                  value={mapping[f.key] || ""}
                  onChange={(e) => {
                    setMapping({ ...mapping, [f.key]: e.target.value });
                    setPreview(null);
                    setTransferConsent(false);
                  }}
                >
                  <option value="">{t("নেবেন না", "Do not copy")}</option>
                  {targetFields
                    .filter((g) => g.type === f.type)
                    .map((g) => (
                      <option key={g.key} value={g.key}>
                        {lang === "bn" ? g.bn : g.en}
                      </option>
                    ))}
                </select>
              </label>
            ))}
            <button
              className="button outline"
              disabled={
                busy || !target || !Object.values(mapping).some(Boolean)
              }
              onClick={() =>
                perform(async () =>
                  setPreview(
                    await api("/api/transfers/preview", {
                      method: "POST",
                      body: JSON.stringify(payload),
                    }),
                  ),
                )
              }
            >
              {t("কী যাবে আগে দেখুন", "Preview selected transfer")}
            </button>
            {preview ? (
              <>
                <DataView value={preview} />
                <label className="consent-check">
                  <input
                    type="checkbox"
                    checked={transferConsent}
                    onChange={(e) => setTransferConsent(e.target.checked)}
                  />
                  <span>
                    {t(
                      "দেখানো তথ্য এই কর্মক্ষেত্রের গন্তব্য টুলের draft-এ নিতে সম্মতি দিচ্ছি।",
                      "I consent to copying the previewed fields into a destination draft in this workspace.",
                    )}
                  </span>
                </label>
                <button
                  className="button dark"
                  disabled={busy || !transferConsent}
                  onClick={() =>
                    perform(async () => {
                      const d = await api<Draft>("/api/transfers", {
                        method: "POST",
                        body: JSON.stringify(payload),
                      });
                      setDrafts([d, ...drafts]);
                      setPreview(null);
                      setTransferConsent(false);
                      setMessage(
                        t(
                          "Draft তৈরি হয়েছে; নিচে খুলুন।",
                          "Draft created. Open it below.",
                        ),
                      );
                    })
                  }
                >
                  {t("সম্মতি দিয়ে draft তৈরি", "Create consented draft")}
                </button>
              </>
            ) : null}
          </section>
        </>
      ) : null}
      <section className="panel">
        <h2>{t("দেওয়া সহায়তার অনুমতি", "Your support grants")}</h2>
        {grants.length ? (
          grants.map((g) => (
            <article className="grant-card" key={g.id}>
              <strong>{g.recipient_email}</strong>
              <p>{g.reason}</p>
              <p>
                {g.fact_keys.join(", ")} ·{" "}
                {new Date(g.expires_at * 1000).toLocaleString(
                  lang === "bn" ? "bn-BD" : "en-GB",
                  { timeZone: "Asia/Dhaka" },
                )}
              </p>
              {g.active ? (
                <button
                  className="button outline small"
                  disabled={busy}
                  onClick={() =>
                    perform(async () => {
                      const next = await api<Grant>(
                        `/api/support/grants/${g.id}/revoke`,
                        { method: "POST" },
                      );
                      setGrants(grants.map((v) => (v.id === g.id ? next : v)));
                    })
                  }
                >
                  {t("এখনই বাতিল", "Revoke now")}
                </button>
              ) : (
                <span>{t("বন্ধ বা মেয়াদ শেষ", "Closed or expired")}</span>
              )}
            </article>
          ))
        ) : (
          <p>{t("কাউকে অনুমতি দেননি।", "No support access granted.")}</p>
        )}
      </section>
      <section className="panel">
        <h2>{t("অন্য টুলের draft", "Cross-tool drafts")}</h2>
        {drafts
          .filter((d) => d.workspace_id === workspaceId)
          .map((d) => (
            <article className="grant-card" key={d.id}>
              <strong>
                {tools.find((x) => x.slug === d.target_module)?.name}
              </strong>
              <p>
                {d.state === "draft"
                  ? t("আপনার পর্যালোচনার অপেক্ষায়", "Awaiting your review")
                  : t("প্রক্রিয়াকরণ সম্পন্ন", "Processed")}
              </p>
              {d.state === "draft" ? (
                <Link
                  className="text-link"
                  href={`/tools/${d.target_module}?transfer=${d.id}`}
                >
                  {t("খুলুন ও যাচাই করুন", "Open and review")}
                </Link>
              ) : null}
            </article>
          ))}
      </section>
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
    </div>
  );
}
