"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Search,
  ArrowRight,
  ShieldCheck,
  Activity,
  ExternalLink,
} from "lucide-react";
import { useApp } from "./context";
import { tools } from "./catalogue";
import { DataView } from "./tool";
const pages: Record<
  string,
  { bn: string; en: string; body_bn: string; body_en: string }
> = {
  about: {
    bn: "একটা কেন্দ্র, বাস্তব কাজের জন্য।",
    en: "One hub for everyday tasks.",
    body_bn:
      "মৌচাক এআই বাংলাদেশের দৈনন্দিন প্রয়োজন নিয়ে তৈরি একটি কেন্দ্রীয় সহায়ক প্ল্যাটফর্ম। কোনো login, signup বা profile ছাড়াই নথি, হিসাব, শেখা ও পর্যবেক্ষণের ৫০টি কর্মক্ষেত্র সরাসরি খোলা যায়।\n\nবর্তমানে বিভিন্ন সহায়ক হিসাব ও রেকর্ডের কাজ, Bengali OCR এবং মৌলিক লেখার উপর রিট্রিভাল যুক্ত করা হচ্ছে। সব টুলের উন্নত AI প্রস্তুত বলে দাবি করা হচ্ছে না। প্রতিটি টুলের সক্ষমতা, প্রক্রিয়ার পরিচয় ও সীমাবদ্ধতা আলাদাভাবে দেখা যায়।\n\nএটি কোনো সরকারি দপ্তর, চিকিৎসক, আইনজীবী বা প্রকৌশলীর বিকল্প নয়। গুরুত্বপূর্ণ সিদ্ধান্তে মূল রেকর্ড ও যোগ্য বিশেষজ্ঞের সহায়তা নিন।",
    body_en:
      "Mouchak AI is a shared support platform built around everyday tasks in Bangladesh. Open 50 tool workspaces for documents, calculations, learning and observations without login, signup or a visitor profile.\n\nThe current implementation combines support calculations and record workflows with Bengali OCR and retrieval over original learning passages. It does not claim that every tool’s advanced AI is ready. Each workspace explains its capabilities, processing identity and limitations.\n\nThe platform is not a government agency or a substitute for a doctor, lawyer or engineer. Check primary records and consult a qualified professional for important decisions.",
  },
  methodology: {
    bn: "ফলাফলের সঙ্গে থাকে প্রক্রিয়ার পরিচয়।",
    en: "Know how a result was produced.",
    body_bn:
      "তথ্য → যাচাই → প্রক্রিয়া → প্রমাণ → ব্যক্তিগত ফলাফল।\n\nসংখ্যার হিসাব দশমিক-নির্ভুল পদ্ধতিতে চলে; সেটিকে AI বলে দেখানো হয় না। OCR-এ Tesseract ব্যবহার হয় এবং মেশিনে পড়া প্রতিটি সংখ্যা নিজে যাচাই করা প্রয়োজন। ShikkhaRAG-এ multilingual MiniLM ও BM25 দিয়ে প্রকল্পের নিজস্ব লেখা থেকে অংশ খোঁজা হয়। এর উত্তর বর্তমানে হুবহু উৎসের অংশ; নতুন লেখা তৈরি করা হয় না।\n\nমডেলের ওজন ডাউনলোড হওয়া মানেই বাংলাদেশে তার নির্ভুলতা প্রমাণিত নয়। উৎপাদনে ব্যবহারের আগে স্থানীয় বৈধ তথ্য, আলাদা মূল্যায়ন সেট, ভুলের পর্যালোচনা ও নির্দিষ্ট release gate প্রয়োজন।\n\nফটো থেকে জমির বৈধতা, পানির নিরাপত্তা, রোগ, ভবনের স্থায়িত্ব বা নিশ্চিত প্রতারণার সিদ্ধান্ত দেওয়া হয় না।",
    body_en:
      "Input → validation → processing → evidence → private result.\n\nNumeric calculations use exact decimal methods and are labelled as calculations. Tesseract performs OCR; users must verify extracted text and digits. ShikkhaRAG combines multilingual MiniLM and BM25 to retrieve project-authored passages. Its current answer is an exact source passage rather than newly generated prose.\n\nDownloaded model weights do not establish accuracy in Bangladesh. Production release needs lawful local examples, a separate evaluation set, error review and a passed release gate.\n\nImages do not establish property ownership, drinking-water safety, diagnosis, structural soundness or proven fraud.",
  },
  privacy: {
    bn: "আপনার তথ্য, আপনার নিয়ন্ত্রণে।",
    en: "Your information, under your control.",
    body_bn:
      "ব্যক্তিগত ফলাফল ও মূল ফাইল ব্যবহারকারীর পরিচয় দিয়ে আলাদা করা হয়। ফাইল ও সংরক্ষিত রেকর্ড এনক্রিপ্ট করা থাকে। সাধারণ অ্যাডমিন ভিউ ব্যক্তিগত স্বাস্থ্য, আইনি, জমি বা শিশুর নথি পড়তে পারে না।\n\nএকটি কাজ প্রক্রিয়াকরণের সম্মতি মডেল প্রশিক্ষণের সম্মতি নয়। এই সংস্করণে ব্যক্তিগত তথ্য কোনো প্রশিক্ষণ করপাসে যায় না। কোনো টুল থেকে অন্য টুলে স্বয়ংক্রিয় তথ্য পাঠানো হয় না।\n\nকর্মক্ষেত্র থেকে ফলাফল ও ফাইল ডাউনলোড বা মুছতে পারবেন। তথ্য ও গোপনীয়তা পাতায় বর্তমান session-এর তথ্য রপ্তানি বা স্পষ্ট সম্মতি দিয়ে মুছে দিতে পারবেন। অপারেটরের এনক্রিপ্ট করা ব্যাকআপের মেয়াদ আলাদা রিটেনশন নীতি মেনে শেষ হবে।\n\nউৎপাদনে চালুর আগে চূড়ান্ত অপারেটর পরিচয়, যোগাযোগ, হোস্টিং অঞ্চল, ব্যাকআপ নীতি এবং আইনগত পর্যালোচনা নির্ধারণ করতে হবে। এই পাতার লেখা প্রাথমিক নীতির খসড়া।",
    body_en:
      "Private results and original files are separated by a private browser-session identifier. Stored records and file bytes are encrypted. General administrator views cannot read private medical, legal, land or child records.\n\nConsent to process a task is not consent to train a model. This release does not add private data to a training corpus. Data is not automatically transferred between tools.\n\nDownload or delete results and files from your workspace. The data controls page exports this session’s data and supports explicitly confirmed clearing. Encrypted operator backups expire under a separate retention policy.\n\nBefore production launch, the operator must finalize its identity, contact details, hosting region, backup policy and legal review. This page is an initial policy draft.",
  },
  terms: {
    bn: "সহায়ক কাজের ব্যবহারের নিয়ম।",
    en: "Terms for support workflows.",
    body_bn:
      "শুধু নিজের বা অনুমতি পাওয়া তথ্য দিন। অন্যের গোপন তথ্য, OTP, পাসওয়ার্ড বা পরিচয়পত্রের অপ্রয়োজনীয় তথ্য দেবেন না। শিশুদের নথি ও কণ্ঠের জন্য যথাযথ অভিভাবকের অনুমতি প্রয়োজন।\n\nগণনা ও ফলাফলে ভুল ইনপুটের প্রভাব থাকে। OCR লেখা নিজে সংশোধন করুন। সরকারি উৎসের প্রার্থী লিংক দেখানো তথ্যের স্বত্ব, অংশীদারত্ব বা সরাসরি সংযোগের দাবি নয়।\n\nগুরুত্বপূর্ণ চিকিৎসা, আইনি, আর্থিক বা নিরাপত্তার সিদ্ধান্তে এই প্ল্যাটফর্মের ফলাফল একমাত্র ভিত্তি করবেন না। কোনো তথ্য নিশ্চিত না হলে মূল কর্তৃপক্ষের সঙ্গে যাচাই করুন।\n\nএই সংস্করণ সীমিত সক্ষমতার উন্নয়ন পর্যায়ে আছে। চূড়ান্ত প্রকাশের আগে কার্যকর শর্তাবলি ও অপারেটর পরিচয় আইনগতভাবে পর্যালোচনা করতে হবে।",
    body_en:
      "Submit only information you own or have permission to use. Avoid other people’s private data, OTPs, passwords and unnecessary identity details. Child records and voice require appropriate guardian permission.\n\nIncorrect inputs affect calculations and outputs. Review and correct OCR. A candidate government reference link does not establish data rights, a partnership or live integration.\n\nDo not use this platform as the sole basis for important medical, legal, financial or safety decisions. Check uncertain information with the original authority.\n\nThis version is under development with limited capabilities. Final enforceable terms and operator identity need legal review before public launch.",
  },
  help: {
    bn: "তিন ধাপে কাজ শুরু করুন।",
    en: "Start a task in three steps.",
    body_bn:
      "১. টুল খুঁজুন: নাম, বিষয় বা সমস্যার ছোট বিবরণ দিয়ে সংগ্রহে খুঁজুন। প্রতিটি টুলে কী এখন কাজ করে এবং কী বাকি, তা দেখুন।\n\n২. নিজের তথ্য দিন: উপযুক্ত ঘরে লেখা বা সংখ্যা লিখুন। সমর্থিত নথি আপলোড করলে OCR-এর খসড়া নিজে সংশোধন করুন। সব সংখ্যার একক ও তারিখ নিশ্চিত করুন।\n\n৩. ফলাফল পর্যালোচনা: প্রক্রিয়ার পরিচয়, হিসাব, মূল উৎস ও সীমাবদ্ধতা দেখুন। সংরক্ষণ, JSON/CSV রপ্তানি বা প্রিন্ট থেকে PDF নিতে পারবেন।\n\nকোনো মডেল বা উৎস প্রস্তুত না থাকলে টুলটি অনুমান করে ফলাফল দেবে না। কোনো login বা signup লাগে না; এই browser session-এ নিজের ফলাফল পাবেন।",
    body_en:
      "1. Find a tool: Search the collection by name, topic or a short description. Review what currently works and what remains unavailable.\n\n2. Enter your information: Use the relevant text or numeric fields. If you upload a supported document, review and correct the OCR draft. Confirm units and dates.\n\n3. Review the result: Check the processing identity, calculations, evidence and limitations. Save, export JSON/CSV, or print to PDF.\n\nWhen a necessary model or source is unavailable, the tool refuses to invent a result. No login or signup is needed; private results belong to the current browser session.",
  },
  contact: {
    bn: "আপনার অভিজ্ঞতা জানান।",
    en: "Tell us about your experience.",
    body_bn:
      "টুলের ভুল, ব্যবহারযোগ্যতার সমস্যা বা উৎসের আপডেট জানান। নিচের ফর্মে ব্যক্তিগত চিকিৎসা, পরিচয়পত্র, পাসওয়ার্ড বা ব্যাংক তথ্য দেবেন না। নাম বা ইমেইল ছাড়া বর্তমান session-এর প্রতিক্রিয়া ব্যক্তিগতভাবে সংরক্ষণ করা হয়।\n\nসরাসরি যোগাযোগের চূড়ান্ত ঠিকানা অপারেটর এখনো নির্ধারণ করেননি।",
    body_en:
      "Report tool errors, usability issues or source updates. Do not include private medical records, identity documents, passwords or bank details in this form. Feedback is stored privately within the current browser session without collecting a name or email.\n\nThe operator has not yet configured a final direct contact address.",
  },
};
export function PublicPage({ page }: { page: string }) {
  const { t, api, user, site } = useApp();
  const [override, setOverride] = useState<Record<string, string>>({}),
    [feedback, setFeedback] = useState(""),
    [message, setMessage] = useState("");
  useEffect(() => {
    fetch("/api/public/cms/" + page)
      .then((r) => (r.ok ? r.json() : {}))
      .then(setOverride)
      .catch(() => {});
  }, [page]);
  const p = pages[page] || pages.about;
  async function send(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api("/api/feedback", {
        method: "POST",
        body: JSON.stringify({ value: { text: feedback } }),
      });
      setMessage(
        t("আপনার মতামত সংরক্ষণ হয়েছে।", "Your feedback has been saved."),
      );
      setFeedback("");
    } catch (e) {
      setMessage((e as Error).message);
    }
  }
  return (
    <article className="page-width prose-page">
      <div className="page-heading">
        <span className="eyebrow">MOUCHAK AI / {page.toUpperCase()}</span>
        <h1>
          {t(
            site.pages[page]?.title.bn || override.title_bn || p.bn,
            site.pages[page]?.title.en || override.title_en || p.en,
          )}
        </h1>
      </div>
      <div className="prose-content">
        {t(
          site.pages[page]?.body.bn || override.body_bn || p.body_bn,
          site.pages[page]?.body.en || override.body_en || p.body_en,
        )
          .split("\n\n")
          .map((s, i) => (
            <p key={i}>{s}</p>
          ))}
      </div>
      {page === "contact" ? (
        <form className="panel" onSubmit={send}>
          <label className="form-field">
            {t("আপনার মতামত", "Your feedback")}
            <textarea
              maxLength={2000}
              required
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
          </label>
          {user ? (
            <button className="button dark">
              {t("মতামত সংরক্ষণ", "Save feedback")}
              <ArrowRight size={17} />
            </button>
          ) : (
            <Link href="/explore">
              {t(
                "Session প্রস্তুত না হলে পৃষ্ঠা refresh করুন",
                "Refresh the page if the session is unavailable",
              )}{" "}
              →
            </Link>
          )}
          {message ? <p role="status">{message}</p> : null}
        </form>
      ) : null}
      <Link className="text-link" href="/explore">
        {t("টুল সংগ্রহ দেখুন", "Explore the tool collection")}
        <ArrowRight size={18} />
      </Link>
    </article>
  );
}
export function SourcesPage() {
  const { t } = useApp();
  const [sources, setSources] = useState<Record<string, unknown>[]>([]),
    [query, setQuery] = useState(""),
    [error, setError] = useState("");
  useEffect(() => {
    fetch("/api/sources")
      .then((r) => {
        if (!r.ok) throw Error("Source register unavailable");
        return r.json();
      })
      .then((d) => setSources(d as Record<string, unknown>[]))
      .catch((e) => setError(e.message));
  }, []);
  const filtered = sources.filter((s) =>
    [s.publisher, s.module_name, s.url]
      .join(" ")
      .toLowerCase()
      .includes(query.toLowerCase()),
  );
  return (
    <div className="page-width sources-page">
      <div className="page-heading">
        <span className="eyebrow">
          {t("স্বচ্ছতার খাতা", "THE TRANSPARENCY REGISTER")}
        </span>
        <h1>{t("তথ্যের উৎস জানুন।", "Know where information comes from.")}</h1>
        <p>
          {t(
            "সরকারি ওয়েবসাইট মানেই প্রশিক্ষণের উন্মুক্ত ডেটাসেট নয়। অনুমতি যাচাই ছাড়া তথ্য আমদানি হয় না।",
            "A public government website is not automatically an open training dataset. Ingestion requires a rights review.",
          )}
        </p>
      </div>
      <div className="source-stats">
        <article>
          <strong>{sources.length || "244"}</strong>
          <span>
            {t("প্রার্থী উৎস-রেফারেন্স", "Candidate source references")}
          </span>
        </article>
        <article>
          <strong>
            {
              sources.filter((s) => s.state === "approved_train_and_reuse")
                .length
            }
          </strong>
          <span>{t("পুনর্ব্যবহারে অনুমোদিত", "Approved for reuse")}</span>
        </article>
        <article>
          <strong>5</strong>
          <span>
            {t("নিজস্ব মৌলিক শিক্ষামূলক পাঠ", "Original learning passages")}
          </span>
        </article>
      </div>
      <div className="notice">
        <ShieldCheck />
        <p>
          {t(
            "উৎসের লিংক থাকা মানে তথ্য ডাউনলোড, লাইসেন্স অনুমোদন বা সরকারি অংশীদারত্ব নয়। তারিখ ও বর্তমান নির্দেশনা মূল প্রকাশকের কাছে যাচাই করুন।",
            "Listing a source does not mean its data has been downloaded, licensed or officially endorsed. Check dates and current instructions with the original publisher.",
          )}
        </p>
      </div>
      <div className="search-box">
        <Search size={20} />
        <input
          aria-label="Search sources"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t(
            "প্রকাশক, বিষয় বা টুল দিয়ে খুঁজুন",
            "Search by publisher, topic or tool",
          )}
        />
        <span>{filtered.length}</span>
      </div>
      {error ? <p className="error">{error}</p> : null}
      <div className="sources-grid">
        {filtered.map((s, i) => (
          <article className="panel source-record" key={i}>
            <span className="eyebrow">
              {String(s.module_name)} · {String(s.id)}
            </span>
            <h3>{String(s.publisher)}</h3>
            <p>{String(s.intended_use)}</p>
            <span className="pill muted">
              {s.state === "candidate"
                ? t(
                    "প্রার্থী · অনুমতি যাচাই বাকি",
                    "Candidate · rights pending",
                  )
                : String(s.state)}
            </span>
            <a href={String(s.url)} target="_blank" rel="noopener noreferrer">
              {t("মূল উৎস দেখুন", "Visit original source")}
              <ExternalLink size={15} />
            </a>
          </article>
        ))}
      </div>
    </div>
  );
}
export function StatusPage() {
  const { t } = useApp();
  const [health, setHealth] = useState<unknown>(null),
    [error, setError] = useState("");
  useEffect(() => {
    fetch("/api/health")
      .then((r) =>
        r.ok
          ? r.json()
          : Promise.reject(Error("Processing service unavailable")),
      )
      .then(setHealth)
      .catch((e) => setError(e.message));
  }, []);
  return (
    <div className="page-width status-page">
      <div className="page-heading">
        <span className="eyebrow">
          {t("বর্তমান সক্ষমতা", "CURRENT READINESS")}
        </span>
        <h1>
          {t(
            "কী কাজ করে, কী যাচাই বাকি।",
            "What works. What still needs review.",
          )}
        </h1>
        <p>
          {t(
            "কোনো সম্পূর্ণ টুলকে উৎপাদন-প্রস্তুত ঘোষণা করা হয়নি। সহায়ক কাজ, মডেল ইনস্টলেশন ও মূল্যায়নের অবস্থা আলাদা।",
            "No complete module is declared production-ready. Support workflows, installed models and evaluation are tracked separately.",
          )}
        </p>
      </div>
      <div className="panel">
        <h2>
          <Activity size={22} />
          {t("সরাসরি সেবার পরীক্ষা", "Live service check")}
        </h2>
        {error ? (
          <p className="error">{error}</p>
        ) : health ? (
          <DataView value={health} />
        ) : (
          <p>{t("সেবা পরীক্ষা চলছে…", "Checking service…")}</p>
        )}
      </div>
      <div className="panel">
        <h2>
          {t("৫০টি টুলের প্রকাশ-অবস্থা", "Release status of all 50 tools")}
        </h2>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>{t("টুল", "Tool")}</th>
                <th>{t("সহায়ক কাজ", "Support workflow")}</th>
                <th>{t("সম্পূর্ণ AI যাচাই", "Full AI validation")}</th>
              </tr>
            </thead>
            <tbody>
              {tools.map((m) => (
                <tr key={m.slug}>
                  <td>
                    <Link href={"/tools/" + m.slug}>{m.name}</Link>
                  </td>
                  <td>
                    {m.release_status === "blocked"
                      ? t("নির্ভরতা বাকি", "Dependency pending")
                      : t("সীমিত কার্যক্রম", "Limited capability")}
                  </td>
                  <td>{t("প্রস্তুত নয়", "Not production-ready")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
