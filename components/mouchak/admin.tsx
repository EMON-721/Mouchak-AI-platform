"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { ShieldCheck, LockKeyhole } from "lucide-react";
import { useApp } from "./context";
import { DataView } from "./tool";
import { OperationsConsole } from "./operations";
import dynamic from "next/dynamic";
const ReadingSpeechLab = dynamic(() =>
  import("./reading-speech").then((m) => m.ReadingSpeechLab),
);
const PipelineOperations = dynamic(() =>
  import("./pipeline-operations").then((m) => m.PipelineOperations),
);
const SiteBuilderEditor = dynamic(() =>
  import("./site-builder").then((m) => m.SiteBuilderEditor),
);
import { DirectoryConsole } from "./directory-console";
import { SignInPrompt } from "./account";
type Obj = Record<string, unknown>;
const tabs = [
  ["overview", "সারসংক্ষেপ", "Overview"],
  ["modules", "টুল পরিচালনা", "Tools"],
  ["site-builder", "সাইট সাজান", "Site Builder"],
  ["cms", "কনটেন্ট ও ব্র্যান্ড", "Content & brand"],
  ["users", "প্রশাসনিক দল", "Operator team"],
  ["sources", "উৎস ও অনুমতি", "Sources & rights"],
  ["models", "মডেল ও মূল্যায়ন", "Models & evaluation"],
  ["reading-speech", "বাংলা speech lab", "Bengali speech lab"],
  ["model-operations", "মডেল নিয়ন্ত্রণ", "Model controls"],
  ["road-data", "সড়ক data review", "Road data review"],
  ["jobs", "ডেটা ইমপোর্ট", "Data imports"],
  ["directories", "সেবার তালিকা", "Service directories"],
  ["audit", "অডিট", "Audit"],
  ["support", "সীমিত সহায়তা", "Support grants"],
  ["publishing", "প্রকাশের সময়সূচি", "Publishing"],
  ["rights", "স্বাধীন rights review", "Asset rights"],
  ["feedback", "মতামত পর্যালোচনা", "Feedback"],
  ["notifications", "সেবার নোটিশ", "Service notices"],
];
export function AdminPage({ tab = "overview" }: { tab?: string }) {
  const { t, user, loading, api } = useApp();
  const [data, setData] = useState<unknown>(null),
    [error, setError] = useState(""),
    [success, setSuccess] = useState(""),
    [page, setPage] = useState("home"),
    [body, setBody] = useState(
      '{\n  "title_bn": "",\n  "title_en": "",\n  "body_bn": "",\n  "body_en": ""\n}',
    ),
    [search, setSearch] = useState(""),
    [selectedSource, setSelectedSource] = useState(""),
    [evidence, setEvidence] = useState(""),
    [state, setState] = useState("rights_review"),
    [raw, setRaw] = useState(""),
    [job, setJob] = useState<Obj | null>(null);
  async function load() {
    setError("");
    try {
      setData(await api("/api/admin/" + tab));
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    if (
      !user ||
      [
        "support",
        "publishing",
        "rights",
        "feedback",
        "notifications",
        "directories",
        "model-operations",
        "road-data",
        "site-builder",
        "reading-speech",
      ].includes(tab)
    )
      return;
    let live = true;
    api("/api/admin/" + tab)
      .then((d) => {
        if (live) setData(d);
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [api, user, tab]);
  async function action(f: () => Promise<unknown>) {
    setError("");
    setSuccess("");
    try {
      await f();
      setSuccess(
        t(
          "কাজ সম্পন্ন এবং অডিটে রেকর্ড হয়েছে।",
          "Completed and recorded in the audit log.",
        ),
      );
      await load();
    } catch (e) {
      setError((e as Error).message);
    }
  }
  if (!user && !loading) return <SignInPrompt />;
  if (loading)
    return (
      <div className="page-width empty">{t("লোড হচ্ছে…", "Loading…")}</div>
    );
  const allowed = !["user", "guardian", "organization_staff", "guest"].includes(
    user?.role || "guest",
  );
  if (!allowed)
    return (
      <div className="page-width empty">
        <LockKeyhole size={40} />
        <h1>
          {t("অনুমোদিত ভূমিকা প্রয়োজন", "An authorized role is required")}
        </h1>
        <p>
          {t(
            "অ্যাকাউন্টের ভূমিকা সার্ভার থেকে নিয়ন্ত্রিত হয়।",
            "Account roles are controlled by the server.",
          )}
        </p>
      </div>
    );
  if (
    [
      "support",
      "publishing",
      "rights",
      "feedback",
      "notifications",
      "directories",
      "model-operations",
      "road-data",
      "site-builder",
      "reading-speech",
    ].includes(tab)
  ) {
    return (
      <div className="page-width admin-layout">
        <aside className="workspace-sidebar">
          {tabs.map(([key, bn, en]) => (
            <Link
              className={key === tab ? "selected" : ""}
              href={"/admin/" + key}
              key={key}
            >
              {t(bn, en)}
            </Link>
          ))}
        </aside>
        <section className="admin-body">
          {tab === "reading-speech" ? (
            <ReadingSpeechLab key={user?.id} />
          ) : tab === "model-operations" || tab === "road-data" ? (
            <PipelineOperations key={user?.id + tab} tab={tab} />
          ) : tab === "site-builder" ? (
            <SiteBuilderEditor key={user?.id} />
          ) : tab === "directories" ? (
            <DirectoryConsole key={user?.id} />
          ) : (
            <OperationsConsole key={`${user?.id}:${tab}`} tab={tab} />
          )}
          <Link href="/admin/security">
            {t("MFA যাচাই ও নিরাপত্তা", "MFA verification & security")}
          </Link>
        </section>
      </div>
    );
  }
  const list = Array.isArray(data) ? (data as Obj[]) : [];
  const filtered = list.filter((x) =>
    JSON.stringify(x).toLowerCase().includes(search.toLowerCase()),
  );
  return (
    <div className="page-width admin-layout">
      <aside className="workspace-sidebar">
        <p className="eyebrow">
          <ShieldCheck size={17} />
          {t("কেন্দ্রীয় প্রশাসন", "CENTRAL ADMIN")}
        </p>
        {tabs.map(([key, bn, en]) => (
          <Link
            key={key}
            className={key === tab ? "selected" : ""}
            href={"/admin/" + key}
          >
            {t(bn, en)}
          </Link>
        ))}
        <div className="aside-note">
          <ShieldCheck />
          <p>
            {t(
              "এখানে ব্যক্তিগত মেডিকেল, জমি বা শিশুর নথি দেখানো হয় না।",
              "Private medical, land and child records are excluded from this console.",
            )}
          </p>
        </div>
      </aside>
      <section className="admin-main">
        <div className="section-heading">
          <div>
            <span className="eyebrow">MOUCHAK CONTROL ROOM</span>
            <h1>
              {t(
                tabs.find((x) => x[0] === tab)?.[1] || "প্রশাসন",
                tabs.find((x) => x[0] === tab)?.[2] || "Administration",
              )}
            </h1>
            <p>
              {t(
                "প্রতিটি পরিবর্তন অনুমতি ও অডিটের অধীন।",
                "Changes require permission and are audited.",
              )}
            </p>
          </div>
          <span className="pill">{user?.role.replaceAll("_", " ")}</span>
        </div>
        {error ? (
          <div className="error" role="alert">
            {error === "MFA_REQUIRED" ? (
              <>
                <strong>{t("আগে MFA যাচাই করুন।", "Verify MFA first.")}</strong>
                <p>
                  {t(
                    "প্রশাসনিক কাজের জন্য গত ১৫ মিনিটে MFA যাচাই আবশ্যক।",
                    "Administrative actions require MFA verified within the last 15 minutes.",
                  )}
                </p>
                <Link href="/admin/security" className="button outline small">
                  {t("নিরাপত্তা সেটিংস", "Security settings")} →
                </Link>
              </>
            ) : (
              error
            )}
          </div>
        ) : null}
        {success ? (
          <p className="success" role="status">
            {success}
          </p>
        ) : null}
        {tab === "overview" && data ? (
          <div className="panel">
            <DataView value={data} />
            <div className="notice">
              <p>
                {t(
                  "এখনো কোনো সম্পূর্ণ AI টুলের উৎপাদন-মানের মূল্যায়ন অনুমোদিত হয়নি।",
                  "No complete AI module has been approved through production evaluation.",
                )}
              </p>
            </div>
          </div>
        ) : null}
        {["modules", "users", "sources", "audit", "jobs"].includes(tab) ? (
          <div className="search-box">
            <input
              aria-label="Search admin records"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t("রেকর্ড খুঁজুন…", "Search records…")}
            />
          </div>
        ) : null}
        {tab === "modules" ? (
          <div className="admin-records">
            {filtered.map((m) => (
              <article key={String(m.slug)} className="panel admin-record">
                <div>
                  <h3>{String(m.name)}</h3>
                  <p>{String(m.slug)}</p>
                  <span className="pill">
                    {t("পূর্ণ AI যাচাই বাকি", "Full AI evaluation pending")}
                  </span>
                </div>
                <div>
                  <button
                    className="button outline small"
                    onClick={() =>
                      action(() =>
                        api("/api/admin/modules/" + m.slug, {
                          method: "PATCH",
                          body: JSON.stringify({
                            value: { enabled: m.enabled === false },
                          }),
                        }),
                      )
                    }
                  >
                    {m.enabled === false
                      ? t("সহায়ক কাজ চালু", "Enable support")
                      : t("সহায়ক কাজ বন্ধ", "Disable support")}
                  </button>
                  <details>
                    <summary>
                      {t(
                        "শিরোনাম ও বর্ণনা সম্পাদনা",
                        "Edit title & description",
                      )}
                    </summary>
                    <ModuleEdit
                      module={m}
                      onSave={(v) =>
                        action(() =>
                          api("/api/admin/modules/" + m.slug, {
                            method: "PATCH",
                            body: JSON.stringify({ value: v }),
                          }),
                        )
                      }
                    />
                  </details>
                </div>
              </article>
            ))}
          </div>
        ) : null}
        {tab === "cms" ? (
          <>
            <section className="panel">
              <h2>{t("নতুন খসড়া তৈরি", "Create a draft")}</h2>
              <p>
                {t(
                  "home, about, privacy, terms, help, contact এবং brand-এর জন্য কাঠামোবদ্ধ বাংলা/ইংরেজি কনটেন্ট। শুধু সাধারণ লেখা; নির্বাহযোগ্য HTML নয়।",
                  "Structured Bengali/English content for home, about, privacy, terms, help, contact and brand. Plain text only; executable HTML is rejected.",
                )}
              </p>
              <label className="form-field">
                {t("পেজ পরিচয়", "Page key")}
                <input value={page} onChange={(e) => setPage(e.target.value)} />
              </label>
              <label className="form-field">
                {t("JSON কনটেন্ট", "JSON content")}
                <textarea
                  className="code-editor"
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                />
              </label>
              <button
                className="button dark"
                onClick={() =>
                  action(() =>
                    api("/api/admin/cms", {
                      method: "POST",
                      body: JSON.stringify({
                        value: { page, body: JSON.parse(body) },
                      }),
                    }),
                  )
                }
              >
                {t("খসড়া সংরক্ষণ", "Save draft")}
              </button>
              <details>
                <summary>{t("ব্র্যান্ডের কীগুলো", "Brand keys")}</summary>
                <p>name_bn, name_en, tagline_bn, tagline_en</p>
              </details>
            </section>
            <section className="panel">
              <h2>{t("সংস্করণ ও রোলব্যাক", "Versions & rollback")}</h2>
              <p>
                {t(
                  "যেকোনো আগের সংস্করণ প্রকাশ করলে সেই কনটেন্ট আবার সক্রিয় হবে।",
                  "Publishing an earlier version makes that content active again.",
                )}
              </p>
              {list.map((v) => (
                <article className="cms-version" key={String(v.id)}>
                  <div>
                    <strong>{String(v.page)}</strong>
                    <small>
                      {String(v.created_at)} · {String(v.status)}
                    </small>
                    <details>
                      <summary>{t("প্রিভিউ", "Preview")}</summary>
                      <DataView value={v.body} />
                    </details>
                  </div>
                  <button
                    className="button outline small"
                    onClick={() =>
                      action(() =>
                        api("/api/admin/cms/" + v.id + "/publish", {
                          method: "POST",
                        }),
                      )
                    }
                  >
                    {t("এই সংস্করণ প্রকাশ", "Publish this version")}
                  </button>
                </article>
              ))}
            </section>
          </>
        ) : null}
        {tab === "users" ? (
          <div className="admin-records">
            {filtered.map((u) => (
              <UserEdit
                key={String(u.id)}
                value={u}
                onSave={(v) =>
                  action(() =>
                    api("/api/admin/users/" + u.id, {
                      method: "PATCH",
                      body: JSON.stringify({ value: v }),
                    }),
                  )
                }
              />
            ))}
          </div>
        ) : null}
        {tab === "sources" ? (
          <>
            <section className="panel">
              <h2>
                {t("উৎসের অনুমতি পর্যালোচনা", "Review source permissions")}
              </h2>
              <label className="form-field">
                {t("উৎস পরিচয়", "Source ID")}
                <input
                  placeholder="SRC-0001"
                  value={selectedSource}
                  onChange={(e) => setSelectedSource(e.target.value)}
                />
              </label>
              <label className="form-field">
                {t("অবস্থা", "State")}
                <select
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                >
                  {[
                    "candidate",
                    "access_review",
                    "rights_review",
                    "approved_reference_only",
                    "approved_train_and_reuse",
                    "quarantined",
                    "revoked",
                  ].map((x) => (
                    <option key={x} value={x}>
                      {x}
                    </option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                {t(
                  "ফাইলভিত্তিক লাইসেন্স, পরিধি ও প্রমাণ",
                  "Asset-level license, scope & evidence",
                )}
                <textarea
                  value={evidence}
                  onChange={(e) => setEvidence(e.target.value)}
                />
              </label>
              <p className="subtle">
                {t(
                  "উচ্চ সংবেদনশীল উৎস পুনর্ব্যবহারের জন্য Asset rights-এ দুই স্বাধীন পর্যালোচনা প্রয়োজন। এই ফর্ম থেকে অনুমোদন দেওয়া যায় না।",
                  "High-sensitivity reuse needs two independent decisions under Asset rights. This form cannot grant that approval.",
                )}
              </p>
              <button
                className="button dark"
                onClick={() =>
                  action(() =>
                    api("/api/admin/sources/" + selectedSource, {
                      method: "PATCH",
                      body: JSON.stringify({ value: { state, evidence } }),
                    }),
                  )
                }
              >
                {t("সিদ্ধান্ত সংরক্ষণ", "Record review")}
              </button>
            </section>
            <div className="admin-records">
              {filtered.map((s) => (
                <article className="panel source-record" key={String(s.id)}>
                  <div className="eyebrow">
                    {String(s.id)} · {String(s.module_id)}
                  </div>
                  <h3>{String(s.publisher)}</h3>
                  <a
                    href={String(s.url)}
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    {String(s.url)} ↗
                  </a>
                  <span className="pill muted">{String(s.state)}</span>
                  <p>{String(s.reuse_license)}</p>
                  <button
                    className="text-link"
                    onClick={() => {
                      setSelectedSource(String(s.id));
                      setEvidence(String(s.evidence || ""));
                      window.scrollTo({ top: 0, behavior: "smooth" });
                    }}
                  >
                    {t("পর্যালোচনা করুন", "Review source")} →
                  </button>
                </article>
              ))}
            </div>
          </>
        ) : null}
        {tab === "models" && data ? (
          <section className="panel">
            <h2>
              {t(
                "চলমান মডেল ও প্রার্থী তালিকা",
                "Runtime models & candidate registry",
              )}
            </h2>
            <p>
              {t(
                "ওজন ফাইল থাকা আর উৎপাদন-মানের মূল্যায়ন পাস করা আলাদা অবস্থা। এখানে মিথ্যা ready ফ্ল্যাগ দেওয়া যায় না।",
                "Having weights installed and passing production evaluation are separate states. This console cannot mark an untested model as ready.",
              )}
            </p>
            <DataView value={(data as Obj).runtime} />
            <details>
              <summary>
                {t(
                  "৫০টি টুলের মূল মডেল প্রয়োজন",
                  "Original model requirements for all 50 tools",
                )}
              </summary>
              <DataView value={(data as Obj).candidates} />
            </details>
          </section>
        ) : null}
        {tab === "jobs" ? (
          <>
            <section className="panel">
              <h2>
                {t(
                  "অনুমোদিত CSV ইমপোর্টের প্রিভিউ",
                  "Preview a permitted CSV import",
                )}
              </h2>
              <p>
                {t(
                  "আগে ডেটা পুনর্ব্যবহারের অনুমতি পর্যালোচনা পাস করতে হবে। প্রিভিউ কোনো প্রকাশিত ডেটাসেট নয়।",
                  "The source must first pass reuse-rights review. A preview does not publish a dataset.",
                )}
              </p>
              <label className="form-field">
                {t("উৎস পরিচয়", "Source ID")}
                <input
                  value={selectedSource}
                  onChange={(e) => setSelectedSource(e.target.value)}
                  placeholder="SRC-0001"
                />
              </label>
              <label className="form-field">
                {t("CSV ডেটা (সর্বোচ্চ ২০০ সারি)", "CSV data (up to 200 rows)")}
                <textarea
                  className="code-editor"
                  value={raw}
                  onChange={(e) => setRaw(e.target.value)}
                />
              </label>
              <button
                className="button outline"
                onClick={() =>
                  action(async () => {
                    setJob(
                      await api<Obj>("/api/admin/datasets/import/dry-run", {
                        method: "POST",
                        body: JSON.stringify({
                          value: { source_id: selectedSource, csv: raw },
                        }),
                      }),
                    );
                  })
                }
              >
                {t("শুধু প্রিভিউ চালান", "Run dry preview")}
              </button>
              {job ? (
                <>
                  <DataView value={job} />
                  <button
                    className="button dark"
                    onClick={() =>
                      action(() =>
                        api(
                          "/api/admin/datasets/import/" +
                            job.job_id +
                            "/approve",
                          { method: "POST" },
                        ),
                      )
                    }
                  >
                    {t(
                      "পরবর্তী যাচাইয়ের জন্য স্টেজ করুন",
                      "Stage for further review",
                    )}
                  </button>
                </>
              ) : null}
            </section>
            <section className="panel">
              <DataView value={filtered} />
              {filtered.map((j) => (
                <button
                  key={String(j.id)}
                  className="button outline small"
                  onClick={() =>
                    action(() =>
                      api("/api/admin/datasets/import/" + j.id + "/rollback", {
                        method: "POST",
                      }),
                    )
                  }
                >
                  {t("রোলব্যাক", "Rollback")} {String(j.id).slice(0, 8)}
                </button>
              ))}
            </section>
          </>
        ) : null}
        {tab === "audit" ? (
          <section className="panel">
            <h2>
              {t("পরিবর্তনের প্রমাণ-শৃঙ্খল", "Hash-linked change history")}
            </h2>
            <p>
              {t(
                "এখানে কোনো ব্যক্তিগত নথির মূল লেখা বা পাসওয়ার্ড নেই।",
                "No raw private document content or passwords appear here.",
              )}
            </p>
            <DataView value={filtered} />
          </section>
        ) : null}
      </section>
    </div>
  );
}
function ModuleEdit({
  module,
  onSave,
}: {
  module: Obj;
  onSave: (v: Obj) => void;
}) {
  const { t } = useApp();
  const [name, setName] = useState(String(module.name)),
    [bn, setBn] = useState(String(module.description_bn)),
    [en, setEn] = useState(String(module.description_en));
  return (
    <div className="module-editor">
      <label className="form-field">
        {t("নাম", "Name")}
        <input value={name} onChange={(e) => setName(e.target.value)} />
      </label>
      <label className="form-field">
        বাংলা
        <textarea value={bn} onChange={(e) => setBn(e.target.value)} />
      </label>
      <label className="form-field">
        English
        <textarea value={en} onChange={(e) => setEn(e.target.value)} />
      </label>
      <button
        className="button outline small"
        onClick={() => onSave({ name, description_bn: bn, description_en: en })}
      >
        {t("সংরক্ষণ", "Save")}
      </button>
    </div>
  );
}
function UserEdit({ value, onSave }: { value: Obj; onSave: (v: Obj) => void }) {
  const { t } = useApp();
  const [role, setRole] = useState(String(value.role));
  return (
    <article className="panel admin-record">
      <div>
        <h3>{String(value.name)}</h3>
        <p>{String(value.email)}</p>
        <small>{value.mfa_enabled ? "MFA enabled" : "MFA not enrolled"}</small>
      </div>
      <div>
        <select
          aria-label="Role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
        >
          {[
            "user",
            "guardian",
            "organization_staff",
            "content_editor",
            "dataset_reviewer",
            "model_operator",
            "support_agent",
            "module_manager",
            "auditor",
            "super_admin",
          ].map((x) => (
            <option key={x} value={x}>
              {x}
            </option>
          ))}
        </select>
        <button
          className="button outline small"
          onClick={() => onSave({ role })}
        >
          {t("ভূমিকা সংরক্ষণ", "Save role")}
        </button>
        <button
          className="button outline small danger"
          onClick={() => onSave({ banned: true })}
        >
          {t("প্রবেশ বন্ধ করুন", "Ban account")}
        </button>
        <button
          className="button outline small"
          onClick={() => onSave({ banned: false })}
        >
          {t("প্রবেশ খুলুন", "Unban")}
        </button>
      </div>
    </article>
  );
}
