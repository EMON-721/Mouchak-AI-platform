"use client";
import { useEffect, useState } from "react";
import { useApp } from "./context";
import { DataView, ResultView } from "./tool";
import type { RunResult } from "./types";

export type BillDraft = {
  draft_fields: Record<string, string | null>;
  candidates: { low_confidence_heuristic: boolean }[];
  redacted_text: string;
  unknown_fields: string[];
  page_count: number;
  model_id: string;
};
type BillType = "electricity" | "gas" | "water" | "internet";
type Fields = {
  month: string;
  period_days: number;
  units: string;
  consumption_bdt: string;
  fixed_bdt: string;
  tax_bdt: string;
  adjustment_bdt: string;
  stated_bdt: string;
};
type BillRow = Fields & {
  id: string;
  is_demo: boolean;
  allow_personal_model: boolean;
  computed_bdt: string;
  difference_bdt: string;
};
type ModelStatus = {
  status: string;
  evaluation_available: boolean;
  eligible_rows: number;
  checksum: string | null;
  card: Record<string, unknown> | null;
};
function defaults(): Fields {
  const parts = new Intl.DateTimeFormat("en", {
    year: "numeric",
    month: "2-digit",
    timeZone: "Asia/Dhaka",
  }).formatToParts(new Date());
  return {
    month: `${parts.find((p) => p.type === "year")!.value}-${parts.find((p) => p.type === "month")!.value}`,
    period_days: 30,
    units: "",
    consumption_bdt: "",
    fixed_bdt: "0",
    tax_bdt: "0",
    adjustment_bdt: "0",
    stated_bdt: "",
  };
}

export default function BillWorkbench({
  workspaceId,
  processingConsent,
  draft: initialDraft,
  assetId,
}: {
  workspaceId: string;
  processingConsent: boolean;
  draft: BillDraft | null;
  assetId?: string;
}) {
  const { api, user, t } = useApp();
  const [kind, setKind] = useState<BillType>("electricity");
  const [fields, setFields] = useState<Fields>(defaults);
  const [rows, setRows] = useState<BillRow[]>([]);
  const [model, setModel] = useState<ModelStatus | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [trainingAllowed, setTrainingAllowed] = useState(false);
  const [trainingConsent, setTrainingConsent] = useState(false);
  const [demo, setDemo] = useState(false);
  const [editing, setEditing] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [result, setResult] = useState<RunResult | null>(null);
  const [pageDraft, setPageDraft] = useState<BillDraft | null>(null);
  const [page, setPage] = useState(1);
  const draft = pageDraft || initialDraft;
  useEffect(() => {
    if (!user || !workspaceId) return;
    const controller = new AbortController();
    const query = new URLSearchParams({
      workspace_id: workspaceId,
      bill_type: kind,
    });
    Promise.all([
      api<BillRow[]>(`/api/bills/history?${query}`, {
        signal: controller.signal,
      }),
      api<ModelStatus>(`/api/bills/model?${query}`, {
        signal: controller.signal,
      }),
    ])
      .then(([bills, status]) => {
        setRows(bills);
        setModel(status);
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(e.message);
      });
    return () => controller.abort();
  }, [api, user, workspaceId, kind]);
  async function reload() {
    const query = new URLSearchParams({
      workspace_id: workspaceId,
      bill_type: kind,
    });
    const [bills, status] = await Promise.all([
      api<BillRow[]>(`/api/bills/history?${query}`),
      api<ModelStatus>(`/api/bills/model?${query}`),
    ]);
    setRows(bills);
    setModel(status);
  }
  function change(key: keyof Fields, value: string) {
    setFields((old) => ({
      ...old,
      [key]: key === "period_days" ? Number(value) : value,
    }));
    setConfirmed(false);
  }
  function payload() {
    return JSON.stringify({
      ...fields,
      workspace_id: workspaceId,
      bill_type: kind,
      confirmed,
      processing_consent: processingConsent,
      allow_personal_model: trainingAllowed,
      is_demo: demo,
    });
  }
  async function save(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api(
        editing ? `/api/bills/history/${editing}` : "/api/bills/history",
        { method: editing ? "PATCH" : "POST", body: payload() },
      );
      await reload();
      setEditing("");
      setConfirmed(false);
      setTrainingConsent(false);
      setNotice(
        t(
          "বিল রাখা হয়েছে। ইতিহাস বদলানোর কারণে আগের ব্যক্তিগত model মুছে দেওয়া হয়েছে।",
          "Bill saved. Changing the baseline removes the previous private model.",
        ),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function train() {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await api("/api/bills/model/train", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: workspaceId,
          bill_type: kind,
          consent: trainingConsent,
        }),
      });
      await reload();
      setNotice(
        t(
          "আপনার নিজস্ব ইতিহাস দিয়ে model তৈরি হয়েছে। এটি বাংলাদেশি holdout-এ যাচাইকৃত নয়।",
          "Your private history model is fitted. It has no validated Bangladesh holdout benchmark.",
        ),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function predict() {
    setBusy(true);
    setError("");
    try {
      setResult(
        await api<RunResult>("/api/bills/predict", {
          method: "POST",
          body: payload(),
        }),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function remove(id: string) {
    if (
      !window.confirm(
        t(
          "এই বিল ও এর ওপর তৈরি ব্যক্তিগত model মুছে যাবে। মুছবেন?",
          "Delete this bill and its derived private model?",
        ),
      )
    )
      return;
    setBusy(true);
    setError("");
    try {
      await api(`/api/bills/history/${id}`, { method: "DELETE" });
      await reload();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function edit(row: BillRow) {
    setEditing(row.id);
    setConfirmed(false);
    setTrainingAllowed(row.allow_personal_model);
    setDemo(row.is_demo);
    setFields({
      month: row.month,
      period_days: row.period_days,
      units: row.units,
      consumption_bdt: row.consumption_bdt,
      fixed_bdt: row.fixed_bdt,
      tax_bdt: row.tax_bdt,
      adjustment_bdt: row.adjustment_bdt,
      stated_bdt: row.stated_bdt,
    });
  }
  async function readPage(value: number) {
    setBusy(true);
    setError("");
    try {
      setPageDraft(
        await api<BillDraft>(`/api/bills/extract/${assetId}?page=${value}`, {
          method: "POST",
        }),
      );
      setPage(value);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const money: [keyof Fields, string, string][] = [
    ["consumption_bdt", "ব্যবহারের চার্জ (৳)", "Consumption charge (BDT)"],
    ["fixed_bdt", "স্থির চার্জ (৳)", "Fixed charge (BDT)"],
    ["tax_bdt", "কর/ভ্যাট (৳)", "Tax/VAT (BDT)"],
    [
      "adjustment_bdt",
      "সমন্বয়/ছাড় (৳; ঋণাত্মক হতে পারে)",
      "Adjustment/rebate (BDT; may be negative)",
    ],
    ["stated_bdt", "বিলে লেখা মোট (৳)", "Stated total (BDT)"],
  ];
  return (
    <details className="panel" open={Boolean(draft)}>
      <summary>
        <strong>
          {t(
            "ছবির খসড়া, বিলের ইতিহাস ও ব্যক্তিগত বিশ্লেষণ",
            "Photo review, bill history & private analysis",
          )}
        </strong>
      </summary>
      <p>
        {t(
          "শুধু নিজের বা অনুমতিপ্রাপ্ত বিল দিন। গ্রাহক নম্বর লাগে না। এই browser session-এর মেয়াদ শেষ হলে ইতিহাস ও model মুছে যাবে।",
          "Use only your own or permitted bills. No customer number is needed. History and model expire with this browser session.",
        )}
      </p>
      {draft ? (
        <section aria-label={t("ছবি থেকে পাওয়া খসড়া", "Extracted draft")}>
          <p>
            {draft.model_id} ·{" "}
            {t(
              "সব সংখ্যা নিজে যাচাই করুন; OCR confidence কোনো নির্ভুলতার সম্ভাবনা নয়।",
              "Verify every number; OCR confidence is not a calibrated accuracy probability.",
            )}
          </p>
          <DataView value={draft.draft_fields} />
          {draft.unknown_fields.length ? (
            <p>
              {t(
                "এই ঘরগুলোর সংখ্যা পাওয়া যায়নি বা অস্পষ্ট: ",
                "Missing or ambiguous fields: ",
              )}
              {draft.unknown_fields.join(", ")}
            </p>
          ) : null}
          <button
            type="button"
            className="button outline small"
            onClick={() => {
              setFields((previous) => ({
                ...previous,
                ...Object.fromEntries(
                  Object.entries(draft.draft_fields).filter(
                    ([, value]) => value !== null,
                  ),
                ),
              }));
              setConfirmed(false);
            }}
          >
            {t("খসড়া সংখ্যা নিচের ঘরে নিন", "Use draft values below")}
          </button>
          <details>
            <summary>
              {t(
                "পরিচয় লুকানো OCR লেখা",
                "OCR text with identifier lines hidden",
              )}
            </summary>
            <p className="data-value">{draft.redacted_text}</p>
          </details>
          {assetId && draft.page_count > 1 ? (
            <div className="row-actions">
              <button
                type="button"
                disabled={busy || page <= 1}
                onClick={() => readPage(page - 1)}
              >
                {t("আগের পৃষ্ঠা", "Previous page")}
              </button>
              <span>
                {page}/{draft.page_count}
              </span>
              <button
                type="button"
                disabled={busy || page >= draft.page_count}
                onClick={() => readPage(page + 1)}
              >
                {t("পরের পৃষ্ঠা", "Next page")}
              </button>
            </div>
          ) : null}
        </section>
      ) : null}
      <form onSubmit={save}>
        <div className="form-field">
          <label htmlFor="bill-kind">{t("বিলের ধরন", "Bill type")}</label>
          <select
            id="bill-kind"
            value={kind}
            disabled={Boolean(editing) || busy}
            onChange={(e) => {
              setKind(e.target.value as BillType);
              setResult(null);
            }}
          >
            <option value="electricity">
              {t("বিদ্যুৎ — kWh", "Electricity — kWh")}
            </option>
            <option value="gas">{t("গ্যাস — m³", "Gas — m³")}</option>
            <option value="water">{t("পানি — m³", "Water — m³")}</option>
            <option value="internet">
              {t("ইন্টারনেট — সংযোগ", "Internet — connection")}
            </option>
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="bill-month">{t("বিলের মাস", "Bill month")}</label>
          <input
            id="bill-month"
            required
            type="month"
            value={fields.month}
            onChange={(e) => change("month", e.target.value)}
          />
        </div>
        <div className="form-field">
          <label htmlFor="bill-days">
            {t("এই বিলের দিনসংখ্যা", "Days covered by this bill")}
          </label>
          <input
            id="bill-days"
            required
            type="number"
            min="1"
            max="62"
            value={fields.period_days}
            onChange={(e) => change("period_days", e.target.value)}
          />
        </div>
        <div className="form-field">
          <label htmlFor="bill-units">
            {t("নিজে নিশ্চিত করা ব্যবহৃত ইউনিট", "Confirmed units consumed")}
          </label>
          <input
            id="bill-units"
            required
            inputMode="decimal"
            value={fields.units}
            onChange={(e) => change("units", e.target.value)}
          />
        </div>
        {money.map(([key, bn, en]) => (
          <div className="form-field" key={key}>
            <label htmlFor={`bill-${key}`}>{t(bn, en)}</label>
            <input
              id={`bill-${key}`}
              required
              inputMode="decimal"
              value={fields[key]}
              onChange={(e) => change(key, e.target.value)}
            />
          </div>
        ))}
        <label className="check-line">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
          />
          {t(
            "বিল দেখে প্রতিটি সংখ্যা যাচাই করেছি।",
            "I checked every number against my bill.",
          )}
        </label>
        <label className="check-line">
          <input
            type="checkbox"
            checked={trainingAllowed}
            onChange={(e) => setTrainingAllowed(e.target.checked)}
          />
          {t(
            "শুধু আমার ব্যক্তিগত model-এর জন্য এই বিল ব্যবহার করতে সম্মতি দিচ্ছি।",
            "Allow this bill to train only my private model.",
          )}
        </label>
        <label className="check-line">
          <input
            type="checkbox"
            checked={demo}
            onChange={(e) => setDemo(e.target.checked)}
          />
          {t(
            "এটি অনুশীলনের তথ্য; model প্রশিক্ষণে যাবে না।",
            "This is practice data; exclude it from model training.",
          )}
        </label>
        {!processingConsent ? (
          <p>
            {t(
              "উপরের প্রক্রিয়াকরণের সম্মতিও প্রয়োজন।",
              "Processing consent above is also required.",
            )}
          </p>
        ) : null}
        <div className="row-actions">
          <button
            className="button outline"
            disabled={busy || !confirmed || !processingConsent || !workspaceId}
          >
            {editing
              ? t("সংশোধন রাখুন", "Save correction")
              : t("ইতিহাসে রাখুন ও হিসাব মিলান", "Save & reconcile bill")}
          </button>
          {editing ? (
            <button
              type="button"
              onClick={() => {
                setEditing("");
                setFields(defaults());
                setConfirmed(false);
              }}
            >
              {t("সংশোধন বাতিল", "Cancel edit")}
            </button>
          ) : null}
          <button
            type="button"
            className="button outline"
            disabled={
              busy || !confirmed || !processingConsent || !model?.checksum
            }
            onClick={predict}
          >
            {t("নিজের ইতিহাসের সঙ্গে তুলনা করুন", "Compare with my history")}
          </button>
        </div>
      </form>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {notice ? <p role="status">{notice}</p> : null}
      <h3>
        {t("নিশ্চিত বিলের ইতিহাস", "Confirmed bill history")} ({rows.length})
      </h3>
      <p>
        {t(
          "চার্জগুলো যোগ করে দেখানো পার্থক্য কোনো ভুল চার্জের অভিযোগ নয়। সরকারি tariff এখানে যাচাই করা হয়নি।",
          "The arithmetic difference is not an allegation of wrong charges. No official tariff has been verified here.",
        )}
      </p>
      {rows.length ? (
        <>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>{t("মাস", "Month")}</th>
                  <th>{t("হিসাবের মোট", "Computed total")}</th>
                  <th>{t("বিলে মোট", "Stated total")}</th>
                  <th>{t("পার্থক্য", "Difference")}</th>
                  <th>{t("নিয়ন্ত্রণ", "Actions")}</th>
                </tr>
              </thead>
              <tbody>
                {rows
                  .slice(-24)
                  .reverse()
                  .map((row) => (
                    <tr key={row.id}>
                      <td>
                        {row.month}
                        {row.is_demo ? " · DEMO" : ""}
                      </td>
                      <td>{row.computed_bdt}</td>
                      <td>{row.stated_bdt}</td>
                      <td>{row.difference_bdt}</td>
                      <td>
                        <button
                          type="button"
                          disabled={busy}
                          onClick={() => edit(row)}
                        >
                          {t("সংশোধন", "Edit")}
                        </button>{" "}
                        <button
                          type="button"
                          disabled={busy}
                          onClick={() => remove(row.id)}
                        >
                          {t("মুছুন", "Delete")}
                        </button>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
          <a
            className="text-link"
            href={`/api/bills/export?${new URLSearchParams({ workspace_id: workspaceId, bill_type: kind })}`}
          >
            {t("বিলের তথ্য ডাউনলোড", "Download bill data")}
          </a>
        </>
      ) : (
        <p>
          {t(
            "এখনও এই ধরনের বিল রাখা হয়নি।",
            "No bills of this type saved yet.",
          )}
        </p>
      )}
      <h3>{t("শুধু আপনার ইতিহাসের model", "A model for your history only")}</h3>
      <p>
        {t(
          "প্রশিক্ষণের উপযোগী নিশ্চিত non-demo বিল: ",
          "Eligible confirmed non-demo bills: ",
        )}
        {model?.eligible_rows ?? 0}/25
      </p>
      <label className="check-line">
        <input
          type="checkbox"
          checked={trainingConsent}
          onChange={(e) => setTrainingConsent(e.target.checked)}
        />
        {t(
          "সম্মতি দেওয়া বিলগুলো দিয়ে ব্যক্তিগত model তৈরি করতে বলছি।",
          "Fit a private model using my individually consented bills.",
        )}
      </label>
      <button
        type="button"
        className="button outline"
        disabled={
          busy ||
          !trainingConsent ||
          (model?.eligible_rows ?? 0) < 25 ||
          !model?.evaluation_available
        }
        onClick={train}
      >
        {busy
          ? t("কাজ চলছে…", "Working…")
          : t("ব্যক্তিগত model তৈরি করুন", "Fit private model")}
      </button>
      {model && !model.evaluation_available ? (
        <p role="status">
          {t(
            "উৎপাদন ব্যবহারে এই ML বন্ধ আছে; বাংলাদেশি holdout ও release review বাকি। বিলের ইতিহাস ও হিসাব ব্যবহার করা যাবে।",
            "ML is disabled in production pending Bangladesh holdouts and release review. Bill history and arithmetic remain available.",
          )}
        </p>
      ) : null}
      {model?.card ? (
        <details>
          <summary>
            {t("মডেল ও training data card", "Model & training data card")}
          </summary>
          <DataView value={model.card} />
        </details>
      ) : null}
      <p>
        {t(
          "বাংলাদেশি holdout যাচাই ও confidence calibration হয়নি। এটি ভবিষ্যৎ বিলের পূর্বাভাস নয়।",
          "No Bangladesh holdout or confidence calibration has passed. This does not forecast future bills.",
        )}
      </p>
      {result ? (
        <ResultView result={result} onDelete={() => setResult(null)} />
      ) : null}
    </details>
  );
}
