"use client";
import { customizeTool } from "./site-config";
import { requestId } from "./request-id";
import type { BillDraft } from "./bill-workbench";
import {
  uploadPrivateFile,
  runQueued,
  type ProcessingJob,
} from "./private-processing";
import { PoseReview, poseDetailSummary } from "./pose-review";
import Link from "next/link";
import Image from "next/image";
import dynamic from "next/dynamic";
const ReadingSpeech = dynamic(() =>
  import("./reading-speech").then((m) => m.ReadingSpeech),
);
const NoiseReview = dynamic(() =>
  import("./noise-review").then((m) => m.NoiseReview),
);
const RoadReferenceLookup = dynamic(() =>
  import("./pipeline-operations").then((m) => m.RoadReferenceLookup),
);
import { useEffect, useState, useRef } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  FileText,
  Upload,
  ShieldCheck,
  Download,
  Trash2,
  Bookmark,
  LoaderCircle,
  Plus,
  X,
  Expand,
  Volume2,
  AlertCircle,
} from "lucide-react";
import fieldData from "@/packages/module-registry/fields.json";
import { tools, categories } from "./catalogue";
import { useApp } from "./context";
import type { Tool, FieldSpec, RunResult, Workspace } from "./types";
function bi(value: string, lang: string) {
  const p = value.split(" / ");
  return p.length === 2 ? (lang === "bn" ? p[1] : p[0]) : value;
}
export function DataView({ value }: { value: unknown }) {
  const { lang, t } = useApp();
  if (value === null || value === undefined)
    return <span className="subtle">—</span>;
  if (typeof value === "boolean")
    return <span>{value ? t("হ্যাঁ", "Yes") : t("না", "No")}</span>;
  if (typeof value === "string" || typeof value === "number")
    return (
      <span className="data-value">
        {typeof value === "string" ? bi(value, lang) : value}
      </span>
    );
  if (Array.isArray(value))
    return value.length ? (
      <div className="data-list">
        {value.map((v, i) => (
          <div key={i} className="data-item">
            <DataView value={v} />
          </div>
        ))}
      </div>
    ) : (
      <span className="subtle">{t("কোনো রেকর্ড নেই", "No records")}</span>
    );
  return (
    <dl className="data-fields">
      {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
        <div key={k}>
          <dt>{label(k, lang)}</dt>
          <dd>
            <DataView value={v} />
          </dd>
        </div>
      ))}
    </dl>
  );
}
const labels: Record<string, string[]> = {
  pose_evidence_available: [
    "Pose-এর যথেষ্ট প্রমাণ আছে",
    "Sufficient pose evidence",
  ],
  sampled_frames: ["বিশ্লেষিত frame", "Sampled frames"],
  tracked_frames: ["Pose পাওয়া frame", "Tracked frames"],
  valid_frame_percentage: ["Pose পাওয়া frame (%)", "Valid frames (%)"],
  duration_seconds: ["দৈর্ঘ্য (সেকেন্ড)", "Duration (seconds)"],
  angle_ranges_2d: ["ছবির সমতলে কোণের সীমা", "Image-plane angle ranges"],
  left_knee_degrees: ["বাঁ হাঁটুর কোণ (ডিগ্রি)", "Left knee (degrees)"],
  right_knee_degrees: ["ডান হাঁটুর কোণ (ডিগ্রি)", "Right knee (degrees)"],
  left_elbow_degrees: ["বাঁ কনুইয়ের কোণ (ডিগ্রি)", "Left elbow (degrees)"],
  right_elbow_degrees: ["ডান কনুইয়ের কোণ (ডিগ্রি)", "Right elbow (degrees)"],
  coaching_suggestions_validated: [
    "Coach-এর পরামর্শ যাচাই হয়েছে",
    "Coaching suggestions validated",
  ],
  minimum: ["সর্বনিম্ন", "Minimum"],
  maximum: ["সর্বোচ্চ", "Maximum"],
  samples: ["নমুনা", "Samples"],
  total_words: ["মোট শব্দ", "Total words"],
  self_marked_difficult_words: [
    "নিজে চিহ্নিত কঠিন শব্দ",
    "Self-marked difficult words",
  ],
  reviewed_words: ["পর্যালোচিত শব্দ", "Reviewed words"],
  comprehension: ["বোঝার অনুশীলন", "Comprehension"],
  your_answer: ["আপনার উত্তর", "Your answer"],
  passage: ["পাঠ", "Passage"],
  basket_lines: ["তালিকার সারি", "Basket lines"],
  fully_covered: ["সব পণ্যের দাম আছে", "Fully covered"],
  known_lines_subtotal_bdt: [
    "জানা দামের উপমোট (৳)",
    "Known lines subtotal (BDT)",
  ],
  missing_prices: ["যেসব দাম নেই", "Missing prices"],
  excluded_observations: ["বাদ দেওয়া দাম", "Excluded observations"],
  lowest_observed_cost_bdt: [
    "দেখা সর্বনিম্ন খরচ (৳)",
    "Lowest observed cost (BDT)",
  ],
  comparable_offers: ["তুলনাযোগ্য দাম", "Comparable offers"],
  basket_cost_bdt: ["তালিকার খরচ (৳)", "Basket cost (BDT)"],
  rejected_observations: ["বাদ দেওয়া পর্যবেক্ষণ", "Rejected observations"],
  vendor: ["বিক্রেতা", "Vendor"],
  occurred_at: ["ঘটনার সময়", "Occurred at"],
  velocity: ["বিক্রির বর্ণনামূলক হার", "Observed sales velocity"],
  minimum_sales: ["ন্যূনতম বিক্রি", "Minimum sales"],
  minimum_distinct_days: ["ন্যূনতম ভিন্ন দিন", "Minimum distinct days"],
  observed_days: ["পর্যবেক্ষণের দিন", "Observed days"],
  net_units_per_day: ["দিনপ্রতি নিট ইউনিট", "Net units per day"],
  ml_forecast: ["ML পূর্বাভাস", "ML forecast"],
  delta: ["পরিমাণ পরিবর্তন", "Quantity change"],
  before: ["আগের পরিমাণ", "Before"],
  after: ["পরের পরিমাণ", "After"],
  events: ["পরিবর্তনের ইতিহাস", "Movements"],

  line_total_bdt: ["চার্জের যোগফল (৳)", "Line total (BDT)"],
  stated_total_bdt: ["বিলে লেখা মোট (৳)", "Stated total (BDT)"],
  difference_bdt: ["পার্থক্য (৳)", "Difference (BDT)"],
  exact_repeated_items: ["একই চার্জ আবার আছে", "Exact repeated items"],
  total_kwh: ["মোট বিদ্যুৎ (kWh)", "Total energy (kWh)"],
  energy_only_cost_bdt: ["এনার্জির খরচ (৳)", "Energy cost only (BDT)"],
  original_value: ["মূল পরিমাণ", "Original value"],
  original_unit: ["মূল একক", "Original unit"],
  decimal: ["শতক / ডেসিমেল", "Decimal"],
  acre: ["একর", "Acre"],
  square_foot: ["বর্গফুট", "Square feet"],
  scenario_total_bdt: ["দৃশ্যপটে মোট (৳)", "Scenario total (BDT)"],
  base_bdt: ["সাধারণ মজুরি (৳)", "Base pay (BDT)"],
  overtime_bdt: ["অতিরিক্ত মজুরি (৳)", "Overtime (BDT)"],
  paid_bdt: ["পেয়েছেন (৳)", "Paid (BDT)"],
  cost_bdt: ["খরচ (৳)", "Cost (BDT)"],
  scenario_revenue_bdt: ["ধরা আয় (৳)", "Scenario revenue (BDT)"],
  scenario_profit_bdt: ["ধরা লাভ/ক্ষতি (৳)", "Scenario profit/loss (BDT)"],
  break_even_unit_price_bdt: [
    "ব্রেক-ইভেন একক মূল্য (৳)",
    "Break-even unit price (BDT)",
  ],
  cash_in_bdt: ["নগদ আয় (৳)", "Cash in (BDT)"],
  cash_out_bdt: ["নগদ ব্যয় (৳)", "Cash out (BDT)"],
  calculated_closing_bdt: ["হিসাবে শেষ নগদ (৳)", "Calculated closing cash"],
  counted_closing_bdt: ["গুনে পাওয়া নগদ (৳)", "Counted closing cash"],
  answer: ["উৎসের লেখা", "Source passage"],
  supported: ["সমর্থনকারী উৎস পাওয়া গেছে", "Supported by evidence"],
  observations: ["রেকর্ডের সংখ্যা", "Observations"],
  unit: ["একক", "Unit"],
  change_first_to_last: ["প্রথম থেকে শেষ পরিবর্তন", "First-to-last change"],
  name: ["নাম", "Name"],
  value: ["মান", "Value"],
  date: ["তারিখ", "Date"],
  recorded_date: ["রেকর্ডের তারিখ", "Recorded date"],
  monthly_bdt: ["মাসিক (৳)", "Monthly (BDT)"],
  annual_recurring_bdt: ["বার্ষিক চলতি খরচ (৳)", "Annual recurring cost"],
  refundable_deposit_bdt: ["ফেরতযোগ্য জামানত (৳)", "Refundable deposit"],
  first_month_cash_bdt: ["প্রথম মাসের নগদ (৳)", "First-month cash"],
  estimated_heat_index_c: [
    "আনুমানিক হিট ইনডেক্স °C",
    "Estimated heat index °C",
  ],
  temperature_c: ["তাপমাত্রা °C", "Temperature °C"],
  humidity_percent: ["আর্দ্রতা %", "Humidity %"],
  matched: ["মিলেছে", "Matched"],
  remaining: ["বাকি আছে", "Remaining"],
  listed_requirements: ["তালিকার শর্ত", "Listed requirements"],
  clause_count: ["শর্তের সংখ্যা", "Clause count"],
  clauses: ["আপনার শর্তগুলো", "Your clauses"],
  diff: ["খসড়ার পার্থক্য", "Draft difference"],
  verbatim_items: ["আপনার মূল লেখা", "Your original text"],
  items: ["আইটেম", "Items"],
  reorder_count: ["পুনরায় কেনার তালিকা", "Reorder count"],
  offers: ["দামের রেকর্ড", "Price records"],
  market: ["বাজার", "Market"],
  unit_price_bdt: ["একক দর (৳)", "Unit price"],
  source: ["উৎস", "Source"],
  confirmed_quantity: ["নিশ্চিত পরিমাণ", "Confirmed quantity"],
  reorder: ["পুনরায় কিনবেন", "Reorder"],
  expiry: ["মেয়াদ", "Expiry"],
  expired: ["মেয়াদ শেষ", "Expired"],
  measurements: ["পরিমাপ", "Measurements"],
  provided_lower: ["আপনার দেওয়া নিম্নসীমা", "Provided lower bound"],
  provided_upper: ["আপনার দেওয়া ঊর্ধ্বসীমা", "Provided upper bound"],
  comparison: ["তুলনা", "Comparison"],
  path: ["পথ", "Path"],
  total_entered_cost: ["নিজের দেওয়া মোট ব্যয়", "Total entered edge cost"],
  explicit_matches: ["লেবেলে শব্দ পাওয়া গেছে", "Explicit label matches"],
  not_found_in_transcription: [
    "এই লেখায় পাওয়া যায়নি",
    "Not found in transcription",
  ],
  confirmed_transcription: ["নিশ্চিত লেবেলের লেখা", "Confirmed label text"],
  indicators: ["যে লক্ষণ পাওয়া গেছে", "Detected indicators"],
  domain_only: ["শুধু ডোমেইন", "Domain only"],
  redacted_text: ["ব্যক্তিগত সংখ্যা সরানো লেখা", "Redacted text"],
  link_opened: ["লিংক খোলা হয়েছে", "Link opened"],
  scenario_cost_bdt: ["ধরা খরচ (৳)", "Scenario cost"],
  scenario_collected_litres: [
    "ধরা সংগৃহীত পানি (লিটার)",
    "Scenario collected litres",
  ],
  document_difference_same_unit: [
    "নথির পার্থক্য, একই একক",
    "Difference in the same unit",
  ],
  note: ["মন্তব্য", "Note"],
  notes: ["মন্তব্য", "Notes"],
  location: ["এলাকা", "Location"],
  measured_ph: ["মাপা pH", "Measured pH"],
  measured_do_mg_l: ["মাপা DO mg/L", "Measured DO mg/L"],
  observation: ["পর্যবেক্ষণ", "Observation"],
  matched_words: ["মেলা শব্দ", "Matched words"],
  expected_words: ["পাঠের শব্দসংখ্যা", "Passage words"],
  typed_words: ["টাইপ করা শব্দ", "Typed words"],
  passage_id: ["পাঠের পরিচয়", "Passage ID"],
  original_passage: ["মূল পাঠ", "Original passage"],
  practice_text: ["অনুশীলনের লেখা", "Practice text"],
  title: ["শিরোনাম", "Title"],
  license: ["লাইসেন্স", "License"],
  publisher: ["প্রকাশক", "Publisher"],
  source_date: ["উৎসের তারিখ", "Source date"],
  official: ["সরকারি উৎস", "Official source"],
  id: ["পরিচয়", "ID"],
  kind: ["ধরন", "Kind"],
};
function label(key: string, lang: string) {
  return labels[key]?.[lang === "bn" ? 0 : 1] || key.replaceAll("_", " ");
}
export function ResultView({
  result,
  onDelete,
}: {
  result: RunResult;
  onDelete?: () => void;
}) {
  const { api, t, lang } = useApp();
  const [busy, setBusy] = useState(false),
    [saved, setSaved] = useState(false),
    [error, setError] = useState("");
  async function save() {
    try {
      await api("/api/runs/" + result.id, {
        method: "PATCH",
        body: JSON.stringify({ value: { saved: !saved } }),
      });
      setSaved(!saved);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function remove() {
    setBusy(true);
    try {
      await api("/api/runs/" + result.id, { method: "DELETE" });
      onDelete?.();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="result-panel" aria-live="polite">
      <div className="result-heading">
        <div className="result-check">
          <Check size={20} />
        </div>
        <div>
          <span className="eyebrow">
            {t("প্রক্রিয়াকরণ সম্পন্ন", "PROCESSING COMPLETE")}
          </span>
          <h2>{t("আপনার সহায়ক ফলাফল", "Your support result")}</h2>
        </div>
      </div>
      <p className="result-method">{bi(result.method, lang)}</p>
      {result.module === "noisetrace-ai" &&
      result.model_version.startsWith("google/yamnet/") ? (
        <NoiseReview result={result} />
      ) : (
        <DataView value={result.facts} />
      )}
      {result.module === "golicoach-ai" ? (
        <PoseReview key={result.id} details={result.details} />
      ) : null}
      <details className="details">
        <summary>
          {t("বিস্তারিত হিসাব ও রেকর্ড", "Detailed calculations & records")}
        </summary>
        <DataView
          value={
            result.module === "golicoach-ai"
              ? poseDetailSummary(result.details)
              : result.details
          }
        />
      </details>
      <div className="result-limits">
        <AlertCircle size={19} />
        <div>
          <strong>
            {t("যে সীমাবদ্ধতা মনে রাখবেন", "Limitations to keep in mind")}
          </strong>
          {result.uncertainties.map((x, i) => (
            <p key={i}>{bi(x, lang)}</p>
          ))}
          <p>
            {t(
              "এই টুলের সম্পূর্ণ উন্নত AI কার্যপ্রবাহ এখনো উৎপাদন ব্যবহারের জন্য যাচাই করা হয়নি।",
              "The tool’s full advanced AI workflow has not passed production validation.",
            )}
          </p>
        </div>
      </div>
      <details className="details">
        <summary>
          {t("উৎস ও প্রক্রিয়ার পরিচয়", "Sources & processing identity")}
        </summary>
        <DataView value={result.references} />
        <p className="mono">{result.model_version}</p>
        <p className="subtle">
          {new Intl.DateTimeFormat(lang === "bn" ? "bn-BD" : "en-BD", {
            timeZone: "Asia/Dhaka",
            dateStyle: "medium",
            timeStyle: "short",
          }).format(new Date(result.created_at))}{" "}
          · {result.latency_ms} ms
        </p>
      </details>
      <div className="result-actions">
        <button className="button outline small" onClick={save}>
          <Bookmark size={16} />
          {saved ? t("সংরক্ষিত", "Saved") : t("সংরক্ষণ", "Save")}
        </button>
        <a
          className="button outline small"
          href={"/api/runs/" + result.id + "/export?format=json"}
        >
          <Download size={16} />
          JSON
        </a>
        <a
          className="button outline small"
          href={"/api/runs/" + result.id + "/export?format=csv"}
        >
          <Download size={16} />
          CSV
        </a>
        <a
          className="button outline small"
          href={"/api/runs/" + result.id + "/export?format=pdf"}
        >
          <FileText size={16} />
          {t("PDF ডাউনলোড", "Download PDF")}
        </a>
        <button className="button outline small" onClick={() => window.print()}>
          {t("প্রিন্ট", "Print")}
        </button>
        <button
          className="button outline small danger"
          disabled={busy}
          onClick={remove}
        >
          <Trash2 size={16} />
          {t("মুছুন", "Delete")}
        </button>
      </div>
      {error ? (
        <p role="alert" className="error">
          {error}
        </p>
      ) : null}
    </section>
  );
}
function RecordTable({
  spec,
  value,
  onChange,
}: {
  spec: FieldSpec;
  value: Record<string, string>[];
  onChange: (v: Record<string, string>[]) => void;
}) {
  const { t } = useApp();
  const cols = spec.columns || [];
  function edit(i: number, k: string, v: string) {
    onChange(value.map((x, j) => (j === i ? { ...x, [k]: v } : x)));
  }
  return (
    <div className="record-editor">
      <div className="table-scroll">
        <table
          aria-describedby={
            spec.help_bn || spec.help_en ? "help-" + spec.key : undefined
          }
        >
          <caption className="sr-only">{t(spec.bn, spec.en)}</caption>
          <thead>
            <tr>
              {cols.map((c) => (
                <th key={c.key} scope="col">
                  {t(c.bn, c.en)}
                  {c.help_bn || c.help_en ? (
                    <small
                      className="table-field-help"
                      id={`help-${spec.key}-${c.key}`}
                    >
                      {t(c.help_bn || "", c.help_en || "")}
                    </small>
                  ) : null}
                </th>
              ))}
              <th>
                <span className="sr-only">{t("মুছুন", "Remove")}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {value.map((row, i) => (
              <tr key={i}>
                {cols.map((c) => (
                  <td key={c.key}>
                    <input
                      aria-label={`${t(c.bn, c.en)} ${i + 1}`}
                      aria-describedby={
                        c.help_bn || c.help_en
                          ? `help-${spec.key}-${c.key}`
                          : undefined
                      }
                      placeholder={t(
                        c.placeholder_bn || spec.placeholder_bn || "",
                        c.placeholder_en || spec.placeholder_en || "",
                      )}
                      type={c.type === "date" ? "date" : "text"}
                      inputMode={c.type === "number" ? "decimal" : undefined}
                      value={row[c.key] || ""}
                      onChange={(e) => edit(i, c.key, e.target.value)}
                    />
                  </td>
                ))}
                <td>
                  <button
                    type="button"
                    className="icon-button danger"
                    aria-label={t("সারি মুছুন", "Remove row")}
                    onClick={() => onChange(value.filter((_, j) => j !== i))}
                  >
                    <X size={16} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button
        type="button"
        className="button outline small"
        onClick={() =>
          onChange([...value, Object.fromEntries(cols.map((c) => [c.key, ""]))])
        }
      >
        <Plus size={16} />
        {t("আরেকটি রেকর্ড", "Add a record")}
      </button>
    </div>
  );
}
const LegacyWorkbench = dynamic(() => import("./legacy-workbench"), {
  ssr: false,
});
const uploadEngines = new Set([
  "image_compare",
  "contract",
  "bill",
  "care",
  "inventory",
  "prices",
  "home",
  "worksite",
  "lab",
  "prescription",
  "vaccine",
  "road",
  "water",
  "form",
  "hospital_bill",
  "land",
  "wage",
  "drain",
  "soil",
  "energy",
  "scam",
  "food",
  "cashbook",
  "audio",
  "video",
]);
const BillWorkbench = dynamic(() => import("./bill-workbench"));

export function ToolWorkspace({ slug }: { slug: string }) {
  const { t, lang, user, loading, api, site } = useApp();
  const initial = tools.find((m) => m.slug === slug);
  const [rawTool, setTool] = useState<Tool | undefined>(initial),
    [inputs, setInputs] = useState<Record<string, unknown>>({}),
    [consent, setConsent] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [result, setResult] = useState<RunResult | null>(null),
    [assetIds, setAssetIds] = useState<string[]>([]),
    [uploadNote, setUploadNote] = useState(""),
    [clipNames, setClipNames] = useState<string[]>([]),
    [ocrText, setOcrText] = useState(""),
    [sources, setSources] = useState<Record<string, unknown>[]>([]),
    [passages, setPassages] = useState<Record<string, string>[]>([]),
    [phrases, setPhrases] = useState<Record<string, string>[]>([]),
    [big, setBig] = useState("");
  const tool = rawTool ? customizeTool(rawTool, site, lang) : undefined;
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspaceId, setWorkspaceId] = useState("");
  const [transferId, setTransferId] = useState("");
  const [billDraft, setBillDraft] = useState<BillDraft | null>(null);
  const [pendingJob, setPendingJob] = useState<ProcessingJob | null>(null);
  const runAbort = useRef<AbortController | null>(null);
  useEffect(() => () => runAbort.current?.abort(), []);
  useEffect(() => {
    if (!user) return;
    let live = true;
    api<Workspace[]>("/api/workspaces")
      .then(async (d) => {
        const requested = new URLSearchParams(window.location.search).get(
          "transfer",
        );
        const draft = requested
          ? await api<{
              id: string;
              state: string;
              target_module: string;
              workspace_id: string;
              inputs: Record<string, unknown>;
            }>("/api/transfers/" + requested)
          : null;
        if (live) {
          setWorkspaces(d);
          if (draft) {
            if (
              draft.state !== "draft" ||
              draft.target_module !== slug ||
              !d.some((w) => w.id === draft.workspace_id)
            )
              throw Error(
                "Transfer unavailable / তথ্য স্থানান্তরের draft পাওয়া যায়নি",
              );
            setWorkspaceId(draft.workspace_id);
            setInputs(draft.inputs);
            setTransferId(draft.id);
          } else setWorkspaceId(d[0]?.id || "");
        }
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [api, user, slug]);
  const file = useRef<HTMLInputElement>(null);
  useEffect(() => {
    let active = true;
    Promise.allSettled([
      fetch("/api/modules/" + slug).then((r) => (r.ok ? r.json() : undefined)),
      fetch("/api/sources?module=" + slug).then((r) => (r.ok ? r.json() : [])),
      fetch("/api/learning").then((r) => (r.ok ? r.json() : [])),
      slug === "shobdosetu-bd"
        ? fetch("/api/phrases").then((r) => r.json())
        : Promise.resolve([]),
    ]).then((res) => {
      if (!active) return;
      if (res[0].status === "fulfilled" && res[0].value)
        setTool(res[0].value as Tool);
      if (res[1].status === "fulfilled")
        setSources(res[1].value as Record<string, unknown>[]);
      if (res[2].status === "fulfilled")
        setPassages(res[2].value as Record<string, string>[]);
      if (res[3].status === "fulfilled")
        setPhrases(res[3].value as Record<string, string>[]);
    });
    return () => {
      active = false;
    };
  }, [slug]);
  if (!tool)
    return (
      <div className="page-width empty">
        <h1>{t("টুল পাওয়া যায়নি", "Tool not found")}</h1>
        <Link href="/explore">{t("সংগ্রহে ফিরুন", "Back to collection")}</Link>
      </div>
    );
  const fields =
    tool.fields ||
    (fieldData as Record<string, FieldSpec[]>)[tool.engine] ||
    [];
  const category =
    site.category_labels[tool.category] || categories[tool.category];
  function change(k: string, v: unknown) {
    setInputs((x) => ({ ...x, [k]: v }));
  }
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const payload = JSON.stringify({
        inputs,
        workspace_id: workspaceId || undefined,
        transfer_id: transferId || undefined,
        consent,
        asset_ids: assetIds,
        language: lang,
        idempotency_key: requestId(),
      });
      const controller = new AbortController();
      runAbort.current = controller;
      const d =
        tool?.execution_mode === "queued"
          ? await runQueued(
              api,
              slug,
              payload,
              controller.signal,
              setPendingJob,
            )
          : await api<RunResult>("/api/tools/" + slug + "/runs", {
              method: "POST",
              body: payload,
              signal: controller.signal,
            });
      setResult(d);
      setTransferId("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
      setPendingJob(null);
    }
  }
  async function upload(files: FileList | null) {
    if (!files?.length) return;
    setBusy(true);
    setError("");
    setUploadNote("");
    try {
      if (!consent)
        throw Error(t("আগে সম্মতি দিন", "Give processing consent first"));
      if (tool?.engine === "video" && files.length > 2)
        throw Error(
          t("সর্বোচ্চ দুটি clip বেছে নিন।", "Choose at most two clips."),
        );
      const ids = [];
      for (const f of Array.from(files).slice(0, 2)) {
        const a = await uploadPrivateFile(api, f, (done, total) =>
          setUploadNote(
            t(
              `ফাইলের ${done}/${total} অংশ পাঠানো হয়েছে`,
              `Uploaded ${done}/${total} file parts`,
            ),
          ),
        );
        ids.push(a.id);
        if (
          tool &&
          tool.engine !== "audio" &&
          tool.engine !== "video" &&
          tool.engine !== "image_compare" &&
          tool.engine !== "drain"
        ) {
          if (tool.slug === "billdetect-ai") {
            setBillDraft(
              await api<BillDraft>("/api/bills/extract/" + a.id, {
                method: "POST",
              }),
            );
          } else {
            const d = await api<{ pages: { text: string }[] }>(
              "/api/assets/" + a.id + "/ocr",
              { method: "POST" },
            );
            setOcrText(d.pages.map((p) => p.text).join("\n\n"));
          }
        }
      }
      setAssetIds(ids);
      setClipNames(
        Array.from(files)
          .slice(0, 2)
          .map((f) => f.name),
      );
      setUploadNote(
        tool?.engine === "video"
          ? t(
              "Clip ব্যক্তিগতভাবে রাখা হয়েছে। প্রথমটি নিজের clip; দ্বিতীয়টি ঐচ্ছিক reference।",
              "Clips stored privately. First: your clip; second: optional reference.",
            )
          : t(
              "ফাইল ব্যক্তিগত ভল্টে রাখা হয়েছে। OCR সংখ্যা ও বানান নিজে যাচাই করুন।",
              "Files stored in your private vault. Check all OCR numbers and spelling yourself.",
            ),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className={"page-width tool-page variant-" + tool.category}>
      <div className="breadcrumbs">
        <Link href="/explore">
          <ArrowLeft size={14} />
          {t("সব টুল", "All tools")}
        </Link>
        <span>/</span>
        <span>{category ? t(category.bn, category.en) : tool.category}</span>
      </div>
      <header className="tool-title">
        <Image unoptimized src={tool.logo} alt="" width="76" height="76" />
        <div>
          <div className="eyebrow">
            MOUCHAK WORKSPACE / {String(tool.number).padStart(2, "0")}
          </div>
          <h1>{tool.name}</h1>
          <p>{t(tool.description_bn, tool.description_en)}</p>
        </div>
        <span className="pill">
          {tool.release_status === "blocked"
            ? t("নির্ভরতা বাকি", "Dependency pending")
            : tool.release_status === "experimental"
              ? t("পরীক্ষামূলক pose", "Experimental pose")
              : t("সীমিত সহায়ক কাজ", "Limited support")}
        </span>
      </header>
      {slug === "roadfix-bd" ? <RoadReferenceLookup /> : null}
      <div className="tool-layout">
        <div className="tool-main">
          <div className="step-strip">
            <span className="current">
              <b>1</b>
              {t("তথ্য দিন", "Enter details")}
            </span>
            <span>
              <b>2</b>
              {t("যাচাই করুন", "Review")}
            </span>
            <span className={result ? "current" : ""}>
              <b>3</b>
              {t("ফলাফল দেখুন", "See results")}
            </span>
          </div>
          {tool.engine === "phraseboard" ? (
            <section className="panel phraseboard">
              <h2>
                {t("এক ট্যাপে প্রয়োজনীয় কথা", "Everyday phrases, one tap away")}
              </h2>
              <p>
                {t(
                  "মাইক্রোফোন ছাড়াই চলে। বড় করে দেখান; ডিভাইসে উপযুক্ত কণ্ঠ থাকলে পড়ে শোনাতে পারেন।",
                  "Works without a microphone. Show large text; speech depends on voices available on your device.",
                )}
              </p>
              <div className="phrase-grid">
                {phrases.map((p, i) => {
                  const values = Object.values(p);
                  const bn =
                    p.bn ||
                    p.text_bn ||
                    p.phrase_bn ||
                    values.find((v) => /[\u0980-\u09ff]/.test(v)) ||
                    "";
                  const en =
                    p.en || p.text_en || p.phrase_en || values[2] || bn;
                  return (
                    <button
                      key={i}
                      onClick={() => {
                        setBig(t(bn, en));
                        change("text", t(bn, en));
                      }}
                    >
                      {t(bn, en)}
                    </button>
                  );
                })}
              </div>
              <textarea
                aria-label={t("নিজের বাক্য লিখুন", "Write your own phrase")}
                value={String(inputs.text || "")}
                onChange={(e) => change("text", e.target.value)}
              />
              <button
                className="button"
                onClick={() => setBig(String(inputs.text || ""))}
              >
                <Expand size={17} />
                {t("বড় করে দেখান", "Show large text")}
              </button>
            </section>
          ) : null}
          {tool.engine === "reading" ? (
            <section className="panel reading-passage">
              <span className="eyebrow">
                {t(
                  "মৌলিক পাঠ · সরকারি পাঠ্যবই নয়",
                  "ORIGINAL PASSAGE · NOT AN OFFICIAL TEXTBOOK",
                )}
              </span>
              {passages
                .filter((p) => p.id === (inputs.passage_id || "AUTH-READ-01"))
                .map((p) => (
                  <div key={p.id}>
                    <h2>{p.title}</h2>
                    <p>{p.text_bn}</p>
                  </div>
                ))}
            </section>
          ) : null}
          {["reading", "inventory", "prices"].includes(tool.engine) ? (
            <LegacyWorkbench
              key={`${user?.id || "public"}:${workspaceId}`}
              tool={tool}
              workspaceId={workspaceId}
              onResult={setResult}
            />
          ) : null}
          {transferId ? (
            <div className="panel" role="status">
              {t(
                "স্থানান্তরের draft প্রস্তুত। নিচের তথ্য ও একক যাচাই করে আলাদা সম্মতি দিয়ে চালান।",
                "Transfer draft loaded. Review the fields and units below, then separately consent to processing.",
              )}
            </div>
          ) : null}
          {tool.engine === "reading" ? (
            <ReadingSpeech
              key={`${user?.id}:${inputs.passage_id || "AUTH-READ-01"}`}
              passageId={String(inputs.passage_id || "AUTH-READ-01")}
              onReviewedText={(text) => change("text", text)}
            />
          ) : null}
          <form className="panel tool-form" onSubmit={submit}>
            {workspaces.length > 1 ? (
              <label className="form-field">
                {t(
                  "ফলাফল কোন কর্মক্ষেত্রে রাখবেন?",
                  "Where should this result be stored?",
                )}
                <select
                  value={workspaceId}
                  onChange={(e) => setWorkspaceId(e.target.value)}
                >
                  {workspaces.map((w) => (
                    <option key={w.id} value={w.id}>
                      {w.name}
                    </option>
                  ))}
                </select>
              </label>
            ) : null}
            <div className="panel-title">
              <span className="number-marker">01</span>
              <div>
                <h2>
                  {t(
                    "আপনার তথ্য দিয়ে শুরু করুন",
                    "Start with your information",
                  )}
                </h2>
                <p>
                  {t(
                    "শুধু নিজের বা অনুমতিপ্রাপ্ত তথ্য দিন।",
                    "Use only your own information or information you have permission to use.",
                  )}
                </p>
              </div>
            </div>
            {tool.release_status === "blocked" ? (
              <div className="notice">
                <AlertCircle size={20} />
                <p>
                  {t(
                    "এই টুলের মূল প্রক্রিয়ার জন্য অনুমোদিত ডেটা বা মূল্যায়িত মডেল প্রয়োজন। বর্তমান অবস্থায় ফলাফল তৈরি বন্ধ রাখা হয়েছে।",
                    "The core workflow needs approved data or an evaluated model. Processing is currently disabled.",
                  )}
                </p>
              </div>
            ) : null}
            {fields.map((spec) => (
              <div className="form-field" key={spec.key}>
                {spec.type === "table" ? (
                  <>
                    <label>{t(spec.bn, spec.en)}</label>
                    <RecordTable
                      spec={spec}
                      value={
                        (inputs[spec.key] as Record<string, string>[]) || []
                      }
                      onChange={(v) => change(spec.key, v)}
                    />
                  </>
                ) : (
                  <>
                    <label htmlFor={"input-" + spec.key}>
                      {t(spec.bn, spec.en)}
                      {spec.optional ? (
                        <small> {t("(ঐচ্ছিক)", "(optional)")}</small>
                      ) : null}
                    </label>
                    {spec.type === "textarea" ? (
                      <textarea
                        id={"input-" + spec.key}
                        placeholder={t(
                          spec.placeholder_bn || "",
                          spec.placeholder_en || "",
                        )}
                        aria-describedby={
                          spec.help_bn || spec.help_en
                            ? "help-" + spec.key
                            : undefined
                        }
                        required={!spec.optional}
                        maxLength={20000}
                        value={String(inputs[spec.key] || "")}
                        onChange={(e) => change(spec.key, e.target.value)}
                      />
                    ) : spec.type === "select" ? (
                      <select
                        id={"input-" + spec.key}
                        aria-describedby={
                          spec.help_bn || spec.help_en
                            ? "help-" + spec.key
                            : undefined
                        }
                        required={!spec.optional}
                        value={String(inputs[spec.key] || "")}
                        onChange={(e) => change(spec.key, e.target.value)}
                      >
                        <option value="">
                          {t(
                            spec.placeholder_bn || "নির্বাচন করুন",
                            spec.placeholder_en || "Choose an option",
                          )}
                        </option>
                        {spec.options?.map((o) => (
                          <option
                            value={o}
                            key={o}
                            disabled={
                              spec.key === "analysis_mode" &&
                              o === "events" &&
                              !tool.noise_runtime?.experimental_enabled
                            }
                          >
                            {spec.key === "analysis_mode"
                              ? o === "events"
                                ? t(
                                    "পরীক্ষামূলক শব্দের ধরন",
                                    "Experimental sound events",
                                  )
                                : t(
                                    "মাপা signal statistics",
                                    "Measured signal statistics",
                                  )
                              : o}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        id={"input-" + spec.key}
                        placeholder={t(
                          spec.placeholder_bn || "",
                          spec.placeholder_en || "",
                        )}
                        aria-describedby={
                          spec.help_bn || spec.help_en
                            ? "help-" + spec.key
                            : undefined
                        }
                        type={spec.type === "date" ? "date" : "text"}
                        inputMode={
                          spec.type === "number" ? "decimal" : undefined
                        }
                        required={!spec.optional}
                        maxLength={spec.type === "number" ? 30 : 200}
                        value={String(inputs[spec.key] || "")}
                        onChange={(e) => change(spec.key, e.target.value)}
                      />
                    )}
                  </>
                )}
                {spec.help_bn || spec.help_en ? (
                  <small id={"help-" + spec.key}>
                    {t(spec.help_bn || "", spec.help_en || "")}
                  </small>
                ) : null}
              </div>
            ))}
            {uploadEngines.has(tool.engine) ? (
              <div className="upload-panel">
                <input
                  ref={file}
                  type="file"
                  className="sr-only"
                  accept={
                    tool.engine === "video"
                      ? "video/mp4,.mp4"
                      : tool.engine === "audio"
                        ? ".wav"
                        : "image/png,image/jpeg,application/pdf"
                  }
                  multiple={
                    tool.engine === "image_compare" ||
                    tool.engine === "drain" ||
                    tool.engine === "video"
                  }
                  onChange={(e) => upload(e.target.files)}
                />
                <Upload size={25} />
                <div>
                  <strong>
                    {tool.engine === "video"
                      ? t(
                          "নিজের clip, চাইলে একটি reference clip",
                          "Your clip and an optional reference clip",
                        )
                      : t(
                          "নথি বা ছবি থেকে শুরু করতে চান?",
                          "Prefer to start with a document?",
                        )}
                  </strong>
                  <p>
                    {tool.engine === "video"
                      ? t(
                          "সর্বোচ্চ ১০ MB, ১০ সেকেন্ড, 1080p, 60 fps; একটি মানুষ। Experimental; কোনো skill/injury score নয়।",
                          "Up to 10 MB, 10 seconds, 1080p, 60 fps; one person. Experimental; no skill/injury score.",
                        )
                      : t(
                          "সর্বোচ্চ ১০ MB · PNG, JPG, PDF; শব্দের জন্য PCM WAV।",
                          "Up to 10 MB · PNG, JPG, PDF; PCM WAV for audio.",
                        )}
                  </p>
                </div>
                <button
                  className="button outline small"
                  type="button"
                  disabled={!user || !consent || busy}
                  onClick={() => file.current?.click()}
                >
                  {t("ফাইল বেছে নিন", "Choose file")}
                </button>
                {uploadNote ? <p className="success">{uploadNote}</p> : null}
                {tool.engine === "video" && clipNames.length ? (
                  <div>
                    <p>
                      {t("নিজের clip", "Your clip")}: {clipNames[0]}
                    </p>
                    {clipNames[1] ? (
                      <>
                        <p>
                          {t("Reference", "Reference")}: {clipNames[1]}
                        </p>
                        <button
                          type="button"
                          className="button outline small"
                          disabled={busy}
                          onClick={() => {
                            setAssetIds((a) => [...a].reverse());
                            setClipNames((a) => [...a].reverse());
                          }}
                        >
                          {t("Clip-এর ক্রম বদলান", "Swap clip order")}
                        </button>
                      </>
                    ) : null}
                  </div>
                ) : null}
              </div>
            ) : null}
            {ocrText ? (
              <div className="form-field">
                <label htmlFor="ocr-review">
                  {t(
                    "OCR খসড়া—নিজে সংশোধন করুন",
                    "OCR draft—review and correct",
                  )}
                </label>
                <textarea
                  id="ocr-review"
                  value={ocrText}
                  onChange={(e) => setOcrText(e.target.value)}
                />
                <button
                  type="button"
                  className="button outline small"
                  onClick={() => change("text", ocrText)}
                >
                  {t("সংশোধিত লেখা ইনপুটে নিন", "Use corrected text as input")}
                </button>
                <p className="subtle">
                  {t(
                    "সংখ্যাভিত্তিক টুলে প্রতিটি সংখ্যা উপরের ঘরে নিজে নিশ্চিত করে দিন।",
                    "For numeric tools, confirm each extracted number in the fields above.",
                  )}
                </p>
              </div>
            ) : null}
            <label className="consent-check">
              <input
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                required
              />
              <span>
                {t(
                  "এই তথ্য ব্যক্তিগতভাবে প্রক্রিয়াকরণের সম্মতি দিচ্ছি। মডেল প্রশিক্ষণে ব্যবহারের সম্মতি দিচ্ছি না।",
                  "I consent to private processing of this information. This does not grant permission for model training.",
                )}
              </span>
            </label>
            {!user && !loading ? (
              <div className="notice">
                <ShieldCheck size={20} />
                <p>
                  {t(
                    "Browser session প্রস্তুত হয়নি। পৃষ্ঠাটি refresh করে আবার চেষ্টা করুন।",
                    "Browser session is unavailable. Refresh this page and retry.",
                  )}{" "}
                  <Link href="/explore">
                    {t("টুলের তালিকা", "Explore tools")} →
                  </Link>
                </p>
              </div>
            ) : null}
            {error ? (
              <div className="error" role="alert">
                {error}
              </div>
            ) : null}
            <button
              className="button dark full"
              disabled={
                !user ||
                busy ||
                !consent ||
                tool.release_status === "blocked" ||
                tool.enabled === false
              }
            >
              {busy ? (
                <LoaderCircle className="spin" size={18} />
              ) : (
                <ArrowRight size={18} />
              )}{" "}
              {busy
                ? t("প্রক্রিয়াকরণ চলছে…", "Processing…")
                : t("পর্যালোচনা ও ফলাফল তৈরি", "Review & process")}
            </button>
            {pendingJob ? (
              <div role="status">
                <p>
                  {pendingJob.state === "queued"
                    ? t("কাজটি অপেক্ষায় আছে।", "Your work is waiting.")
                    : t(
                        "কাজটি প্রক্রিয়াকরণ হচ্ছে।",
                        "Your work is processing.",
                      )}
                </p>
                <Link href="/work">
                  {t("এই session-এর কাজ দেখুন", "View session work")}
                </Link>
                <button
                  type="button"
                  className="text-link"
                  onClick={async () => {
                    try {
                      await api(`/api/jobs/${pendingJob.id}/cancel`, {
                        method: "POST",
                      });
                    } catch (e) {
                      setError((e as Error).message);
                    }
                  }}
                >
                  {t("কাজ বাতিল করুন", "Cancel work")}
                </button>
              </div>
            ) : null}
            <p className="form-footnote">
              <ShieldCheck size={14} />
              {t(
                "আপনার ফলাফল অন্য ব্যবহারকারী বা প্রশাসকের সাধারণ ভিউতে যাবে না।",
                "Your results stay out of other users’ and administrators’ general views.",
              )}
            </p>
          </form>
          {result ? (
            <ResultView result={result} onDelete={() => setResult(null)} />
          ) : null}
          {slug === "billdetect-ai" ? (
            <BillWorkbench
              key={assetIds[0] || "manual"}
              workspaceId={workspaceId}
              processingConsent={consent}
              draft={billDraft}
              assetId={assetIds[0]}
            />
          ) : null}
        </div>
        <aside className="tool-context">
          <section className="context-card">
            <div className="context-icon">
              <ShieldCheck size={24} />
            </div>
            <h3>{t("শুরুতেই সীমাবদ্ধতা জানুন", "Know the limits first")}</h3>
            <p>
              {lang === "bn"
                ? tool.safety
                : "This workspace offers a limited support workflow. Its full specialized AI pipeline is not production-validated. Verify important decisions with a qualified professional."}
            </p>
            <div className="rule-line" />
            <span className="eyebrow">{t("প্রক্রিয়া", "PROCESSING")}</span>
            <p>
              {t(
                "নিয়ম/হিসাব যেখানে প্রযোজ্য। OCR ও রিট্রিভাল থাকলে প্রকৃত মডেলের পরিচয় ফলাফলে থাকবে।",
                "Rules and calculations where applicable. OCR and retrieval identify the actual model in their outputs.",
              )}
            </p>
          </section>
          <section className="context-card sources">
            <h3>
              <FileText size={18} />
              {t("উৎস ও রেফারেন্স", "Sources & references")}
            </h3>
            <p>
              {t(
                "নিচের লিংকগুলো প্রার্থী রেফারেন্স। ডেটা আমদানি বা প্রশিক্ষণের অনুমতি নিশ্চিত নয়।",
                "These are candidate references. Permission for ingestion or training is not established.",
              )}
            </p>
            {sources.slice(0, 4).map((s, i) => (
              <a
                key={i}
                target="_blank"
                rel="noopener noreferrer"
                href={String(s.url)}
              >
                <strong>{String(s.publisher)}</strong>
                <span>{t("অনুমতি যাচাই বাকি", "Rights review pending")} ↗</span>
              </a>
            ))}
            <Link href="/sources">
              {t("সম্পূর্ণ উৎস তালিকা", "Full source register")}
              <ArrowRight size={14} />
            </Link>
          </section>
          <section className="context-card">
            <h3>{t("সব কাজ এক জায়গায়", "Everything in one place")}</h3>
            <p>
              {t(
                "আগের ফলাফল, ব্যক্তিগত ফাইল ও গোপনীয়তার নিয়ন্ত্রণ আপনার কর্মক্ষেত্রে।",
                "Find past results, private files and privacy controls in your workspace.",
              )}
            </p>
            <Link className="text-link" href="/work">
              {t("আমার কাজ", "My workspace")}
              <ArrowRight size={16} />
            </Link>
          </section>
        </aside>
      </div>
      {big ? (
        <div
          className="phrase-overlay"
          role="dialog"
          aria-modal="true"
          aria-label={t("বড় অক্ষরে বাক্য", "Large text phrase")}
        >
          <button
            autoFocus
            className="icon-button"
            aria-label="Close"
            onClick={() => setBig("")}
          >
            <X />
          </button>
          <p>{big}</p>
          <button
            className="button"
            onClick={() => {
              if ("speechSynthesis" in window) {
                const voice = new SpeechSynthesisUtterance(big);
                voice.lang = lang === "bn" ? "bn-BD" : "en-GB";
                window.speechSynthesis.speak(voice);
              }
            }}
          >
            <Volume2 size={18} />
            {t("ডিভাইসের কণ্ঠে পড়ুন", "Read with device voice")}
          </button>
          <button className="button outline" onClick={() => setBig("")}>
            {t("ফিরুন", "Back")}
          </button>
        </div>
      ) : null}
    </div>
  );
}
