"use client";
import { requestId } from "./request-id";
import { useEffect, useState, useCallback } from "react";
import {
  Plus,
  Trash2,
  BookOpen,
  Store,
  ShoppingBasket,
  ArrowRight,
} from "lucide-react";
import { useApp } from "./context";
import { DataView } from "./tool";
import type { Tool, RunResult } from "./types";
const enteredNumber = (value: string) =>
  Number(
    value
      .replace(/[০-৯]/g, (d) => String("০১২৩৪৫৬৭৮৯".indexOf(d)))
      .replace(/,/g, ""),
  );
type Props = {
  tool: Tool;
  workspaceId: string;
  onResult: (r: RunResult) => void;
};
type Passage = {
  id: string;
  title: string;
  text: string;
  question: string;
  publisher: string;
  license: string;
  level: number;
};
type Commodity = { id: string; name: string; aliases: string[]; unit: string };
type Item = {
  id: string;
  name: string;
  sku: string;
  unit: string;
  quantity: number;
  minimum: number;
  revision: number;
  reorder: boolean;
  expired: boolean;
};
export default function LegacyWorkbench(p: Props) {
  if (p.tool.engine === "reading") return <ReadingStudio {...p} />;
  if (p.tool.engine === "inventory") return <StockBook {...p} />;
  if (p.tool.engine === "prices") return <BasketDesk {...p} />;
  return null;
}
function Consent({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  const { t } = useApp();
  return (
    <label className="consent-check">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        required
      />
      <span>
        {t(
          "এই কাজের জন্য ব্যক্তিগত প্রক্রিয়াকরণে সম্মতি দিচ্ছি; গবেষণা বা মডেল প্রশিক্ষণের অনুমতি নয়।",
          "I consent to private processing for this task, not research or model training.",
        )}
      </span>
    </label>
  );
}
function ReadingStudio({ workspaceId, onResult }: Props) {
  const { t, user, api, lang } = useApp();
  const [passages, setPassages] = useState<Passage[]>([]),
    [id, setId] = useState(""),
    [selected, setSelected] = useState<number[]>([]),
    [answer, setAnswer] = useState(""),
    [consent, setConsent] = useState(false),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    let active = true;
    fetch("/api/reading/passages")
      .then((r) => {
        if (!r.ok) throw Error("Reading library unavailable");
        return r.json();
      })
      .then((d) => {
        if (active) {
          const rows = d as Passage[];
          setPassages(rows);
          setId(rows[0]?.id || "");
        }
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, []);
  const passage = passages.find((p) => p.id === id);
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      onResult(
        await api<RunResult>("/api/tools/banglaread-coach/runs", {
          method: "POST",
          body: JSON.stringify({
            workspace_id: workspaceId || undefined,
            consent,
            language: lang,
            inputs: { passage_id: id, difficult_indices: selected, answer },
            idempotency_key: requestId(),
          }),
        }),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel legacy-workbench reading-studio">
      <span className="eyebrow">
        <BookOpen size={18} />
        {t("আগের পাঠাগারের কেন্দ্রীয় সংস্করণ", "INTEGRATED READING LIBRARY")}
      </span>
      <h2>{t("পড়ি, শব্দ বাছি, ভাবি।", "Read, choose words, reflect.")}</h2>
      <p>
        {t(
          "কঠিন মনে হওয়া শব্দে চাপ দিন। এটি নিজের অনুশীলন—উচ্চারণের AI নম্বর নয়।",
          "Tap words you find difficult. This is reflective practice, not an AI pronunciation score.",
        )}
      </p>
      <label className="form-field">
        {t("পাঠ বাছুন", "Choose a passage")}
        <select
          value={id}
          onChange={(e) => {
            setId(e.target.value);
            setSelected([]);
            setAnswer("");
          }}
        >
          {passages.map((p) => (
            <option key={p.id} value={p.id}>
              {p.title} · {t("ধাপ", "Level")} {p.level}
            </option>
          ))}
        </select>
      </label>
      {passage ? (
        <>
          <div
            className="reading-word-canvas"
            aria-label={t("কঠিন শব্দ চিহ্নিত করুন", "Mark difficult words")}
          >
            {passage.text
              .normalize("NFC")
              .split(/\s+/)
              .map((word, i) => (
                <button
                  key={i}
                  type="button"
                  aria-pressed={selected.includes(i)}
                  onClick={() =>
                    setSelected((v) =>
                      v.includes(i) ? v.filter((n) => n !== i) : [...v, i],
                    )
                  }
                >
                  {word}
                </button>
              ))}
          </div>
          <p className="subtle">
            {t("চিহ্নিত শব্দ", "Marked words")}: {selected.length} ·{" "}
            {passage.publisher} · {passage.license}
          </p>
          <form onSubmit={save}>
            <label className="form-field">
              {passage.question}
              <input
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                maxLength={500}
                placeholder={t(
                  "ইচ্ছা হলে নিজের ভাষায় লিখুন",
                  "Optional: write your answer",
                )}
              />
            </label>
            <Consent checked={consent} onChange={setConsent} />
            <button
              className="button dark"
              disabled={!user || !workspaceId || !consent || busy}
            >
              {busy
                ? t("সংরক্ষণ হচ্ছে…", "Saving…")
                : t("অনুশীলন পর্যালোচনা ও সংরক্ষণ", "Review & save practice")}
              <ArrowRight size={16} />
            </button>
          </form>
        </>
      ) : null}
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {!user ? (
        <p className="subtle">
          {t(
            "Session প্রস্তুত হলে সরাসরি অনুশীলন সংরক্ষণ করুন; অ্যাকাউন্ট লাগে না।",
            "Save practice once the browser session is ready; no account is needed.",
          )}
        </p>
      ) : null}
    </section>
  );
}
type BasketRow = {
  product: string;
  quantity: string;
  unit: string;
  price_type: string;
  grade: string;
  origin: string;
};
type Offer = BasketRow & {
  price: string;
  vendor: string;
  market: string;
  date: string;
};
const initialBasket = (): BasketRow => ({
  product: "",
  quantity: "1",
  unit: "kg",
  price_type: "retail",
  grade: "unspecified",
  origin: "unspecified",
});
const today = () =>
  new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Dhaka",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
function BasketDesk({ workspaceId, onResult }: Props) {
  const { t, api, user, lang } = useApp();
  const [dictionary, setDictionary] = useState<Commodity[]>([]),
    [basket, setBasket] = useState<BasketRow[]>([initialBasket()]),
    [offers, setOffers] = useState<Offer[]>([]),
    [days, setDays] = useState("7"),
    [consent, setConsent] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    fetch("/api/commodities")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => {
        if (active) setDictionary(d as Commodity[]);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);
  function productName(p: Commodity) {
    return lang === "bn" ? p.name : p.aliases[0] || p.name;
  }
  function edit<T extends BasketRow>(
    rows: T[],
    setter: (v: T[]) => void,
    index: number,
    key: string,
    value: string,
  ) {
    setter(
      rows.map((r, i) => {
        if (i !== index) return r;
        const next = { ...r, [key]: value };
        if (key === "product")
          next.unit =
            dictionary.find((d) => d.name === value)?.unit || next.unit;
        return next;
      }),
    );
  }
  async function compare(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      onResult(
        await api<RunResult>("/api/tools/bazarcompare-ai/runs", {
          method: "POST",
          body: JSON.stringify({
            workspace_id: workspaceId || undefined,
            consent,
            language: lang,
            inputs: { mode: "basket", basket, offers, freshness_days: days },
            idempotency_key: requestId(),
          }),
        }),
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  function rowFields<T extends BasketRow>(
    row: T,
    index: number,
    list: T[],
    setter: (v: T[]) => void,
  ) {
    return (
      <>
        <label>
          {t("পণ্য", "Product")}
          <select
            value={row.product}
            required
            onChange={(e) =>
              edit(list, setter, index, "product", e.target.value)
            }
          >
            <option value="">{t("বাছুন", "Choose")}</option>
            {dictionary.map((p) => (
              <option key={p.id} value={p.name}>
                {productName(p)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t("পরিমাণ", "Quantity")}
          <input
            required
            inputMode="decimal"
            value={row.quantity}
            onChange={(e) =>
              edit(list, setter, index, "quantity", e.target.value)
            }
          />
        </label>
        <label>
          {t("একক", "Unit")}
          <select
            value={row.unit}
            onChange={(e) => edit(list, setter, index, "unit", e.target.value)}
          >
            {["kg", "g", "l", "ml", "piece", "dozen"].map((u) => (
              <option key={u}>{u}</option>
            ))}
          </select>
        </label>
        <label>
          {t("দামের ধরন", "Price type")}
          <select
            value={row.price_type}
            onChange={(e) =>
              edit(list, setter, index, "price_type", e.target.value)
            }
          >
            <option value="retail">{t("খুচরা", "Retail")}</option>
            <option value="wholesale">{t("পাইকারি", "Wholesale")}</option>
          </select>
        </label>
        <label>
          {t("মান/গ্রেড", "Grade")}
          <input
            required
            value={row.grade}
            maxLength={80}
            onChange={(e) => edit(list, setter, index, "grade", e.target.value)}
          />
        </label>
        <label>
          {t("উৎপত্তি/ধরন", "Origin/type")}
          <input
            required
            value={row.origin}
            maxLength={80}
            onChange={(e) =>
              edit(list, setter, index, "origin", e.target.value)
            }
          />
        </label>
      </>
    );
  }
  return (
    <section className="panel legacy-workbench">
      <span className="eyebrow">
        <ShoppingBasket size={18} />
        {t(
          "নিজের দেখা দাম দিয়ে বাজারের তালিকা",
          "PRIVATE OBSERVED-PRICE BASKET",
        )}
      </span>
      <h2>
        {t("একই মান, একই ধরনের দাম তুলনা।", "Compare like-for-like prices.")}
      </h2>
      <p>
        {t(
          "পণ্যের অভিধানে বাজারদর নেই। দাম নিজে যোগ করুন। খুচরা/পাইকারি, মান ও উৎপত্তি আলাদা হলে একই তুলনায় যাবে না।",
          "The product dictionary contains no prices. Add your own observations. Retail/wholesale, grade and origin must match.",
        )}
      </p>
      <form onSubmit={compare}>
        <h3>{t("কী কিনবেন?", "Your shopping list")}</h3>
        {basket.map((row, i) => (
          <div className="legacy-row" key={i}>
            {rowFields(row, i, basket, setBasket)}
            <button
              type="button"
              className="icon-button danger"
              aria-label={t("তালিকার সারি মুছুন", "Remove basket line")}
              onClick={() => setBasket(basket.filter((_, j) => j !== i))}
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
        <button
          type="button"
          className="button outline small"
          onClick={() => setBasket([...basket, initialBasket()])}
        >
          <Plus size={16} />
          {t("পণ্য যোগ করুন", "Add product")}
        </button>
        <div className="rule-line" />
        <h3>{t("নিজের দেখা দামের রেকর্ড", "Your dated price observations")}</h3>
        {offers.map((row, i) => (
          <div className="legacy-row offer-row" key={i}>
            {rowFields(row, i, offers, setOffers)}
            {(["price", "vendor", "market", "date"] as const).map((k, j) => (
              <label key={k}>
                {
                  [
                    t("দাম (৳)", "Price (BDT)"),
                    t("দোকান", "Vendor"),
                    t("বাজার", "Market"),
                    t("দেখার তারিখ", "Observed date"),
                  ][j]
                }
                <input
                  type={k === "date" ? "date" : "text"}
                  inputMode={k === "price" ? "decimal" : undefined}
                  required
                  value={row[k]}
                  onChange={(e) =>
                    edit(offers, setOffers, i, k, e.target.value)
                  }
                />
              </label>
            ))}
            <button
              type="button"
              className="icon-button danger"
              aria-label={t("দামের রেকর্ড মুছুন", "Remove price observation")}
              onClick={() => setOffers(offers.filter((_, j) => j !== i))}
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
        <button
          type="button"
          className="button outline small"
          onClick={() =>
            setOffers([
              ...offers,
              {
                ...initialBasket(),
                price: "",
                vendor: "",
                market: "",
                date: today(),
              },
            ])
          }
        >
          <Plus size={16} />
          {t("দেখা দাম যোগ করুন", "Add observed price")}
        </button>
        <label className="form-field freshness-field">
          {t(
            "সর্বোচ্চ কত দিনের পুরোনো দাম তুলনায় নেবেন?",
            "Maximum age of an observation (days)",
          )}
          <input
            inputMode="numeric"
            value={days}
            onChange={(e) => setDays(e.target.value)}
            required
          />
        </label>
        <Consent checked={consent} onChange={setConsent} />
        <button
          className="button dark"
          disabled={!user || !consent || !workspaceId || busy}
        >
          {t("তুলনা ও ব্যক্তিগত রিপোর্ট", "Compare & save private report")}
          <ArrowRight size={16} />
        </button>
        {error ? (
          <p role="alert" className="error">
            {error}
          </p>
        ) : null}
      </form>
    </section>
  );
}
function StockBook({ workspaceId }: Props) {
  const { t, user, api } = useApp();
  const [items, setItems] = useState<Item[]>([]),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [consent, setConsent] = useState(false),
    [draft, setDraft] = useState({
      name: "",
      sku: "",
      unit: "packet",
      quantity: "0",
      minimum: "0",
      unit_cost: "",
      expiry: "",
    }),
    [movement, setMovement] = useState({
      item_id: "",
      type: "sale",
      quantity: "1",
      date: today(),
    }),
    [history, setHistory] = useState<unknown>(null);
  const load = useCallback(async () => {
    if (!user || !workspaceId) return;
    const rows = await api<Item[]>("/api/retail/" + workspaceId + "/items");
    setItems(rows);
  }, [api, user, workspaceId]);
  useEffect(() => {
    if (!user || !workspaceId) return;
    let active = true;
    api<Item[]>("/api/retail/" + workspaceId + "/items")
      .then((d) => {
        if (active) setItems(d);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [api, user, workspaceId]);
  async function perform(action: () => Promise<unknown>) {
    setError("");
    setBusy(true);
    try {
      await action();
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const current = items.find((i) => i.id === movement.item_id);
  return (
    <section className="panel legacy-workbench">
      <span className="eyebrow">
        <Store size={18} />
        {t("ব্যক্তিগত স্টক খাতা", "PRIVATE STOCK LEDGER")}
      </span>
      <h2>
        {t(
          "নিশ্চিত স্টক, লেনদেনের ইতিহাস।",
          "Confirmed stock, traceable movements.",
        )}
      </h2>
      <p>
        {t(
          "ছবি দেখে অদেখা স্টক অনুমান করা হয় না। প্রতিটি বিক্রি, কেনা ও ফেরত আলাদা রেকর্ড হবে।",
          "No unseen stock is inferred from a photo. Sales, purchases and returns create separate records.",
        )}
      </p>
      {!user ? (
        <p>
          {t(
            "স্টক খাতার browser session প্রস্তুত হচ্ছে।",
            "Preparing a private browser session for the stock book.",
          )}
        </p>
      ) : (
        <>
          <Consent checked={consent} onChange={setConsent} />
          <details>
            <summary>
              {t(
                "নতুন পণ্য ও শুরুতে গোনা স্টক",
                "Add product & counted opening stock",
              )}
            </summary>
            <form
              className="stock-create"
              onSubmit={(e) => {
                e.preventDefault();
                void perform(async () => {
                  await api("/api/retail/" + workspaceId + "/items", {
                    method: "POST",
                    body: JSON.stringify({
                      ...draft,
                      quantity: enteredNumber(draft.quantity),
                      minimum: enteredNumber(draft.minimum),
                      unit_cost: draft.unit_cost || null,
                      expiry: draft.expiry || null,
                      consent,
                    }),
                  });
                  setDraft({
                    ...draft,
                    name: "",
                    sku: "",
                    quantity: "0",
                    expiry: "",
                  });
                });
              }}
            >
              {(
                [
                  "name",
                  "sku",
                  "quantity",
                  "minimum",
                  "unit_cost",
                  "expiry",
                ] as const
              ).map((k, i) => (
                <label key={k} className="form-field">
                  {
                    [
                      t("পণ্যের নাম", "Product name"),
                      "SKU",
                      t("গোনা শুরুর স্টক", "Counted opening quantity"),
                      t("রিঅর্ডার সীমা", "Reorder threshold"),
                      t(
                        "এককের ক্রয়মূল্য (৳, ঐচ্ছিক)",
                        "Unit cost (BDT, optional)",
                      ),
                      t(
                        "নিশ্চিত মেয়াদ (ঐচ্ছিক)",
                        "Confirmed expiry (optional)",
                      ),
                    ][i]
                  }
                  <input
                    required={!["unit_cost", "expiry"].includes(k)}
                    type={k === "expiry" ? "date" : "text"}
                    inputMode={
                      ["quantity", "minimum", "unit_cost"].includes(k)
                        ? "decimal"
                        : undefined
                    }
                    value={draft[k]}
                    onChange={(e) =>
                      setDraft({ ...draft, [k]: e.target.value })
                    }
                  />
                </label>
              ))}
              <label className="form-field">
                {t("গোনার একক", "Counted unit")}
                <select
                  value={draft.unit}
                  onChange={(e) => setDraft({ ...draft, unit: e.target.value })}
                >
                  {["packet", "piece", "kg", "g", "l", "ml"].map((u) => (
                    <option key={u}>{u}</option>
                  ))}
                </select>
              </label>
              <p className="subtle">
                {t(
                  "এ সংস্করণে পূর্ণসংখ্যার গোনা একক ব্যবহৃত হয়।",
                  "This version records whole counted units.",
                )}
              </p>
              <button
                className="button dark"
                disabled={!consent || !workspaceId || busy}
              >
                {t("পণ্য সংরক্ষণ", "Save product")}
              </button>
            </form>
          </details>
          <div className="table-scroll stock-table">
            <table>
              <thead>
                <tr>
                  <th>{t("পণ্য", "Product")}</th>
                  <th>{t("নিশ্চিত স্টক", "Confirmed stock")}</th>
                  <th>{t("অবস্থা", "Status")}</th>
                  <th>{t("ইতিহাস", "History")}</th>
                </tr>
              </thead>
              <tbody>
                {items.map((i) => (
                  <tr key={i.id}>
                    <td>
                      {i.name}
                      <small className="stock-sku">{i.sku}</small>
                    </td>
                    <td>
                      {i.quantity} {i.unit}
                    </td>
                    <td>
                      {i.expired
                        ? t("মেয়াদ শেষ", "Expired")
                        : i.reorder
                          ? t("রিঅর্ডার সীমায়", "At reorder threshold")
                          : t("লগ করা আছে", "Recorded")}
                    </td>
                    <td>
                      <button
                        type="button"
                        className="text-link"
                        onClick={() =>
                          perform(async () =>
                            setHistory(
                              await api(
                                "/api/retail/" +
                                  workspaceId +
                                  "/items/" +
                                  i.id +
                                  "/history",
                              ),
                            ),
                          )
                        }
                      >
                        {t("দেখুন", "View")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!items.length ? (
              <p className="subtle">
                {t(
                  "এখনো পণ্য নেই। নিজের গোনা স্টক দিয়ে শুরু করুন।",
                  "No products yet. Start with your counted stock.",
                )}
              </p>
            ) : null}
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!current) return;
              void perform(async () => {
                await api(
                  "/api/retail/" +
                    workspaceId +
                    "/items/" +
                    current.id +
                    "/movements",
                  {
                    method: "POST",
                    body: JSON.stringify({
                      type: movement.type,
                      quantity: enteredNumber(movement.quantity),
                      date: movement.date,
                      expected_revision: current.revision,
                      idempotency_key: requestId(),
                      consent,
                    }),
                  },
                );
                setHistory(null);
              });
            }}
          >
            <h3>{t("স্টকের পরিবর্তন লিখুন", "Record a stock movement")}</h3>
            <div className="legacy-row">
              <label>
                {t("পণ্য", "Product")}
                <select
                  value={movement.item_id}
                  required
                  onChange={(e) =>
                    setMovement({ ...movement, item_id: e.target.value })
                  }
                >
                  <option value="">{t("বাছুন", "Choose")}</option>
                  {items.map((i) => (
                    <option key={i.id} value={i.id}>
                      {i.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("ধরন", "Type")}
                <select
                  value={movement.type}
                  onChange={(e) =>
                    setMovement({ ...movement, type: e.target.value })
                  }
                >
                  {[
                    ["sale", t("বিক্রি", "Sale")],
                    ["purchase", t("কেনা", "Purchase")],
                    ["return", t("ক্রেতার ফেরত", "Customer return")],
                    ["damage", t("নষ্ট", "Damage")],
                    [
                      "supplier_return",
                      t("সরবরাহকারীকে ফেরত", "Supplier return"),
                    ],
                  ].map(([k, v]) => (
                    <option key={k} value={k}>
                      {v}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {t("পরিমাণ", "Quantity")}
                <input
                  required
                  inputMode="numeric"
                  value={movement.quantity}
                  onChange={(e) =>
                    setMovement({ ...movement, quantity: e.target.value })
                  }
                />
              </label>
              <label>
                {t("ঘটনার তারিখ", "Movement date")}
                <input
                  type="date"
                  required
                  max={today()}
                  value={movement.date}
                  onChange={(e) =>
                    setMovement({ ...movement, date: e.target.value })
                  }
                />
              </label>
            </div>
            <button
              className="button dark"
              disabled={!consent || !workspaceId || !current || busy}
            >
              {t("লেনদেন রেকর্ড করুন", "Record movement")}
            </button>
          </form>
          {history ? (
            <details open className="details">
              <summary>
                {t(
                  "এই পণ্যের লেনদেন ও পর্যবেক্ষিত বিক্রি",
                  "Movement history & observed sales",
                )}
              </summary>
              <DataView value={history} />
            </details>
          ) : null}
        </>
      )}
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
    </section>
  );
}
