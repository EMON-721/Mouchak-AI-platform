"use client";
import { useEffect, useState } from "react";
import { useApp } from "./context";

type Copy = { bn: string; en: string };
type Lesson = {
  lesson_id: string;
  source_seed_id: string | null;
  title: Copy;
  passage: string;
  level: number;
  topic: Copy;
  age_band: "general" | "new_reader" | "child_or_new_reader";
  educational_goal: Copy;
  question: Copy;
  options: Copy[];
  correct_option_index: number;
  explanation: Copy;
  publisher: string;
  license: "CC0-1.0" | "CC-BY-4.0" | "CC-BY-SA-4.0" | "permission_granted";
  rights_note: string;
};
type Version = {
  id: string;
  lesson_id: string;
  title: Copy;
  author: string;
  created_at: string;
  status: string;
};
type Detail = {
  id: string;
  lesson: Lesson;
  author: string;
  previously_published: boolean;
  review: { decision: string; reason: string; reviewer: string } | null;
};
type Library = {
  state: {
    revision: string | null;
    lessons: Record<string, { version: string; order: number }>;
  };
  versions: Version[];
  seeds: { id: string; title: string }[];
  published: {
    id: string;
    title: string;
    title_en: string;
    level: number;
    revision: string;
  }[];
};
const fresh = (): Lesson => ({
  lesson_id: "OWN-",
  source_seed_id: null,
  title: { bn: "", en: "" },
  passage: "",
  level: 1,
  topic: { bn: "", en: "" },
  age_band: "new_reader",
  educational_goal: { bn: "", en: "" },
  question: { bn: "", en: "" },
  options: [
    { bn: "", en: "" },
    { bn: "", en: "" },
  ],
  correct_option_index: 0,
  explanation: { bn: "", en: "" },
  publisher: "",
  license: "permission_granted",
  rights_note: "",
});
const checkLabels = [
  ["spelling", "বানান যাচাই", "Spelling checked"],
  ["age_suitability", "পাঠকের বয়সের উপযোগী", "Suitable for the reader band"],
  [
    "answer_grounded_in_passage",
    "উত্তর পাঠের তথ্য থেকে পাওয়া যায়",
    "Answer grounded in the passage",
  ],
  ["educational_goal", "শিক্ষার লক্ষ্য যাচাই", "Educational goal checked"],
  [
    "publication_rights",
    "প্রকাশের অনুমতি যাচাই",
    "Publication rights verified",
  ],
];
const emptyChecks = () =>
  Object.fromEntries(checkLabels.map(([key]) => [key, false]));

export function ReadingContentEditor() {
  const { api, t, user, lang } = useApp();
  const [data, setData] = useState<Library | null>(null);
  const [lesson, setLesson] = useState<Lesson>(fresh);
  const [selected, setSelected] = useState<Detail | null>(null);
  const [seed, setSeed] = useState("BRP001");
  const [checks, setChecks] = useState<Record<string, boolean>>(emptyChecks);
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [dragged, setDragged] = useState<string | null>(null);
  useEffect(() => {
    let live = true;
    api<Library>("/api/admin/reading-content")
      .then((v) => {
        if (live) setData(v);
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [api]);
  function edit<K extends keyof Lesson>(key: K, value: Lesson[K]) {
    setLesson((v) => ({ ...v, [key]: value }));
    setSelected(null);
    setChecks(emptyChecks());
  }
  async function action(fn: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await fn();
      setData(await api<Library>("/api/admin/reading-content"));
      setMessage(
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
  async function open(id: string) {
    const d = await api<Detail>(`/api/admin/reading-content/drafts/${id}`);
    setLesson(d.lesson);
    setSelected(d);
    setChecks(emptyChecks());
    setReason("");
  }
  async function loadSeed() {
    const d = await api<{
      passage: {
        passage_id: string;
        title: string;
        passage: string;
        level: number;
        topic: string;
      };
      question: {
        question_bn: string;
        options_bn: string[];
        correct_option_index: number;
      };
    }>(`/api/admin/reading-content/seeds/${seed}`);
    setLesson({
      ...fresh(),
      lesson_id: d.passage.passage_id,
      source_seed_id: d.passage.passage_id,
      title: { bn: d.passage.title, en: "" },
      passage: d.passage.passage,
      level: d.passage.level,
      topic: { bn: d.passage.topic, en: "" },
      question: { bn: d.question.question_bn, en: "" },
      options: d.question.options_bn.map((bn) => ({ bn, en: "" })),
      correct_option_index: d.question.correct_option_index,
    });
    setSelected(null);
    setChecks(emptyChecks());
    setReason("");
  }
  function bilingual(
    key: "title" | "topic" | "educational_goal" | "question" | "explanation",
    bn: string,
    en: string,
  ) {
    return (
      <fieldset>
        <legend>{t(bn, en)}</legend>
        {(["bn", "en"] as const).map((language) => (
          <label className="form-field" key={language}>
            {language === "bn" ? "বাংলা" : "English"}
            <input
              lang={language}
              required
              maxLength={key === "title" ? 160 : 600}
              value={lesson[key][language]}
              onChange={(e) =>
                edit(key, { ...lesson[key], [language]: e.target.value })
              }
            />
          </label>
        ))}
      </fieldset>
    );
  }
  const ordered = data
    ? Object.entries(data.state.lessons)
        .sort((a, b) => a[1].order - b[1].order)
        .map(([id]) => id)
    : [];
  async function move(id: string, target: string) {
    if (!data || id === target) return;
    const a = data.published.find((p) => p.id === "lesson:" + id),
      b = data.published.find((p) => p.id === "lesson:" + target);
    if (!a || !b || a.level !== b.level) return;
    const list = ordered.filter((x) => x !== id);
    list.splice(list.indexOf(target), 0, id);
    await action(() =>
      api("/api/admin/reading-content/order", {
        method: "POST",
        body: JSON.stringify({
          expected_revision: data.state.revision,
          lesson_ids: list,
        }),
      }),
    );
  }
  async function step(id: string, offset: number) {
    const p = data?.published.find((x) => x.id === "lesson:" + id);
    const same =
      data?.published
        .filter((x) => x.level === p?.level)
        .map((x) => x.id.slice(7)) || [];
    const index = same.indexOf(id),
      target = same[index + offset];
    if (target) {
      // Swap positions for keyboard moves; all active IDs remain in the payload.
      const list = [...ordered],
        a = list.indexOf(id),
        b = list.indexOf(target);
      [list[a], list[b]] = [list[b], list[a]];
      await action(() =>
        api("/api/admin/reading-content/order", {
          method: "POST",
          body: JSON.stringify({
            expected_revision: data!.state.revision,
            lesson_ids: list,
          }),
        }),
      );
    }
  }
  return (
    <div className="reading-content-editor">
      <span className="eyebrow">{t("বাংলা পাঠাগার", "READING LIBRARY")}</span>
      <h1>
        {t("লিখুন, যাচাই করুন, প্রকাশ করুন", "Write, review and publish")}
      </h1>
      <p>
        {t(
          "মূল kit-এর ১২০টি পাঠ ও প্রশ্ন review ছাড়া প্রকাশিত হয় না। প্রতিটি সংস্করণে আলাদা সম্পাদকের পাঁচটি যাচাই ও প্রকাশের অনুমতি প্রয়োজন।",
          "The 120 original seed passages and questions stay unpublished until reviewed. Every version needs five independent editorial checks and publication rights.",
        )}
      </p>
      {error && (
        <p role="alert" className="error-message">
          {error}
        </p>
      )}
      {message && <p role="status">{message}</p>}
      {!data ? (
        <p>{t("পাঠাগার লোড হচ্ছে…", "Loading library…")}</p>
      ) : (
        <>
          <section className="panel">
            <h2>{t("মূল পাঠ থেকে খসড়া", "Draft from a preserved seed")}</h2>
            <label className="form-field">
              {t("মূল পাঠ", "Original seed")}
              <select
                value={seed}
                disabled={busy}
                onChange={(e) => setSeed(e.target.value)}
              >
                {data.seeds.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.id} · {s.title}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="button"
              disabled={busy}
              onClick={() => action(loadSeed)}
            >
              {t("সম্পাদনার জন্য খুলুন", "Load for editing")}
            </button>{" "}
            <button
              type="button"
              className="button"
              disabled={busy}
              onClick={() => {
                setLesson(fresh());
                setSelected(null);
                setChecks(emptyChecks());
                setReason("");
              }}
            >
              {t("নিজের নতুন পাঠ", "New original lesson")}
            </button>
          </section>
          <form
            className="panel"
            onSubmit={(e) => {
              e.preventDefault();
              action(async () => {
                const d = await api<{ id: string }>(
                  "/api/admin/reading-content/drafts",
                  {
                    method: "POST",
                    body: JSON.stringify({
                      expected_revision: data.state.revision,
                      lesson,
                    }),
                  },
                );
                await open(d.id);
              });
            }}
          >
            <h2>{t("পাঠ সম্পাদনা", "Lesson editor")}</h2>
            <fieldset disabled={busy}>
              <label className="form-field">
                {t("পাঠের পরিচয়", "Lesson ID")}
                <input
                  required
                  pattern="(BRP[0-9]{3}|OWN-[A-Za-z0-9-]{1,40})"
                  value={lesson.lesson_id}
                  readOnly={!!lesson.source_seed_id}
                  onChange={(e) => edit("lesson_id", e.target.value)}
                />
              </label>
              {lesson.source_seed_id && (
                <p>
                  {t("মূল পাঠের পরিচয়", "Preserved source")}:{" "}
                  {lesson.source_seed_id}
                </p>
              )}
              {bilingual("title", "শিরোনাম", "Title")}
              <label className="form-field">
                {t(
                  "বাংলা পাঠ: সর্বোচ্চ ২৫০ শব্দ",
                  "Bengali passage: at most 250 words",
                )}
                <textarea
                  lang="bn"
                  required
                  minLength={10}
                  maxLength={4000}
                  rows={6}
                  value={lesson.passage}
                  onChange={(e) => edit("passage", e.target.value)}
                />
              </label>
              <label className="form-field">
                {t("ধাপ", "Level")}
                <select
                  value={lesson.level}
                  onChange={(e) => edit("level", Number(e.target.value))}
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n}>{n}</option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                {t("পাঠকের ধরন", "Reader band")}
                <select
                  value={lesson.age_band}
                  onChange={(e) =>
                    edit("age_band", e.target.value as Lesson["age_band"])
                  }
                >
                  <option value="general">{t("সাধারণ", "General")}</option>
                  <option value="new_reader">
                    {t("নতুন পাঠক", "New reader")}
                  </option>
                  <option value="child_or_new_reader">
                    {t(
                      "শিশু বা নতুন পাঠকের জন্য উপযুক্ত পাঠ",
                      "Text suitable for children or new readers",
                    )}
                  </option>
                </select>
              </label>
              {bilingual("topic", "বিষয়", "Topic")}
              {bilingual(
                "educational_goal",
                "শিক্ষার লক্ষ্য",
                "Educational goal",
              )}
              {bilingual(
                "question",
                "পাঠ থেকে প্রশ্ন",
                "Comprehension question",
              )}
              <fieldset>
                <legend>{t("উত্তরের বিকল্প", "Answer options")}</legend>
                {lesson.options.map((option, i) => (
                  <fieldset key={i}>
                    <legend>{i + 1}</legend>
                    {(["bn", "en"] as const).map((language) => (
                      <label className="form-field" key={language}>
                        {language === "bn" ? "বাংলা" : "English"}
                        <input
                          lang={language}
                          required
                          maxLength={600}
                          value={option[language]}
                          onChange={(e) =>
                            edit(
                              "options",
                              lesson.options.map((o, index) =>
                                index === i
                                  ? { ...o, [language]: e.target.value }
                                  : o,
                              ),
                            )
                          }
                        />
                      </label>
                    ))}
                  </fieldset>
                ))}
                <button
                  type="button"
                  disabled={lesson.options.length >= 6}
                  onClick={() =>
                    edit("options", [...lesson.options, { bn: "", en: "" }])
                  }
                >
                  {t("বিকল্প যোগ", "Add option")}
                </button>{" "}
                <button
                  type="button"
                  disabled={lesson.options.length <= 2}
                  onClick={() => {
                    edit("options", lesson.options.slice(0, -1));
                    edit(
                      "correct_option_index",
                      Math.min(
                        lesson.correct_option_index,
                        lesson.options.length - 2,
                      ),
                    );
                  }}
                >
                  {t("শেষ বিকল্প বাদ", "Remove last option")}
                </button>
              </fieldset>
              <label className="form-field">
                {t("সঠিক উত্তর", "Correct answer")}
                <select
                  value={lesson.correct_option_index}
                  onChange={(e) =>
                    edit("correct_option_index", Number(e.target.value))
                  }
                >
                  {lesson.options.map((_, i) => (
                    <option value={i} key={i}>
                      {i + 1}
                    </option>
                  ))}
                </select>
              </label>
              {bilingual(
                "explanation",
                "উত্তরের ব্যাখ্যা",
                "Answer explanation",
              )}
              <label className="form-field">
                {t("প্রকাশক", "Publisher")}
                <input
                  required
                  minLength={2}
                  maxLength={160}
                  value={lesson.publisher}
                  onChange={(e) => edit("publisher", e.target.value)}
                />
              </label>
              <label className="form-field">
                {t("প্রকাশের লাইসেন্স", "Publication licence")}
                <select
                  value={lesson.license}
                  onChange={(e) =>
                    edit("license", e.target.value as Lesson["license"])
                  }
                >
                  {[
                    "permission_granted",
                    "CC0-1.0",
                    "CC-BY-4.0",
                    "CC-BY-SA-4.0",
                  ].map((l) => (
                    <option key={l}>{l}</option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                {t(
                  "অধিকার ও অনুমতির প্রমাণ/রেফারেন্স",
                  "Rights evidence or permission reference",
                )}
                <textarea
                  required
                  minLength={10}
                  maxLength={2000}
                  value={lesson.rights_note}
                  onChange={(e) => edit("rights_note", e.target.value)}
                />
              </label>
              <button className="button dark" type="submit">
                {t("নতুন অপরিবর্তনীয় খসড়া রাখুন", "Save a new immutable draft")}
              </button>
            </fieldset>
          </form>
          <section className="panel">
            <h2>
              {t("সংস্করণ ও স্বাধীন review", "Versions and independent review")}
            </h2>
            <label className="form-field">
              {t("সংরক্ষিত সংস্করণ খুলুন", "Open a saved version")}
              <select
                disabled={busy}
                value={selected?.id || ""}
                onChange={(e) => {
                  if (e.target.value) action(() => open(e.target.value));
                }}
              >
                <option value="">{t("বাছুন", "Choose")}</option>
                {data.versions.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.lesson_id} · {v.title[lang]} · {v.status} ·{" "}
                    {new Intl.DateTimeFormat(
                      lang === "bn" ? "bn-BD" : "en-GB",
                      {
                        timeZone: "Asia/Dhaka",
                        dateStyle: "medium",
                        timeStyle: "short",
                      },
                    ).format(new Date(v.created_at))}
                  </option>
                ))}
              </select>
            </label>
            {selected && (
              <fieldset disabled={busy}>
                <p>
                  {t(
                    "উপরের ফর্মে এই সংস্করণের সম্পূর্ণ পাঠ ও উত্তর দেখা যাচ্ছে। সম্পাদনা করলে নতুন খসড়া প্রয়োজন।",
                    "The complete saved lesson and answer are shown above. Editing requires a new draft.",
                  )}
                </p>
                {selected.review ? (
                  <p>
                    {t("Review সিদ্ধান্ত", "Review decision")}:{" "}
                    {selected.review.decision} · {selected.review.reason}
                  </p>
                ) : (
                  <>
                    {selected.author === user?.id && (
                      <p>
                        {t(
                          "আপনার খসড়া অন্য সম্পাদক review করবেন।",
                          "A different editor must review your draft.",
                        )}
                      </p>
                    )}
                    {checkLabels.map(([key, bn, en]) => (
                      <label className="consent-check" key={key}>
                        <input
                          type="checkbox"
                          checked={checks[key]}
                          disabled={selected.author === user?.id}
                          onChange={(e) =>
                            setChecks((v) => ({
                              ...v,
                              [key]: e.target.checked,
                            }))
                          }
                        />
                        {t(bn, en)}
                      </label>
                    ))}
                  </>
                )}
                <label className="form-field">
                  {t(
                    "সিদ্ধান্তের কারণ: অন্তত ১০ অক্ষর",
                    "Decision reason: at least 10 characters",
                  )}
                  <textarea
                    minLength={10}
                    maxLength={1000}
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                  />
                </label>
                {!selected.review &&
                  (["approved", "rejected"] as const).map((decision) => (
                    <button
                      type="button"
                      className="button"
                      key={decision}
                      disabled={
                        reason.trim().length < 10 ||
                        selected.author === user?.id ||
                        (decision === "approved" &&
                          !Object.values(checks).every(Boolean))
                      }
                      onClick={() =>
                        action(async () => {
                          await api(
                            `/api/admin/reading-content/drafts/${selected.id}/review`,
                            {
                              method: "POST",
                              body: JSON.stringify({
                                decision,
                                checks,
                                reason,
                              }),
                            },
                          );
                          await open(selected.id);
                        })
                      }
                    >
                      {decision === "approved"
                        ? t("অনুমোদন দিন", "Approve")
                        : t("সংশোধন প্রয়োজন", "Reject for revision")}
                    </button>
                  ))}
                {selected.review?.decision === "approved" && (
                  <>
                    <button
                      type="button"
                      className="button dark"
                      disabled={reason.trim().length < 10}
                      onClick={() =>
                        action(async () => {
                          await api(
                            `/api/admin/reading-content/drafts/${selected.id}/publish`,
                            {
                              method: "POST",
                              body: JSON.stringify({
                                expected_revision: data.state.revision,
                                reason,
                                rollback: false,
                              }),
                            },
                          );
                          await open(selected.id);
                        })
                      }
                    >
                      {t("প্রকাশ করুন", "Publish")}
                    </button>{" "}
                    <button
                      type="button"
                      className="button"
                      disabled={
                        !selected.previously_published ||
                        reason.trim().length < 10
                      }
                      onClick={() =>
                        action(async () => {
                          await api(
                            `/api/admin/reading-content/drafts/${selected.id}/publish`,
                            {
                              method: "POST",
                              body: JSON.stringify({
                                expected_revision: data.state.revision,
                                reason,
                                rollback: true,
                              }),
                            },
                          );
                          await open(selected.id);
                        })
                      }
                    >
                      {t(
                        "আগের প্রকাশিত সংস্করণ ফেরান",
                        "Restore a previously published version",
                      )}
                    </button>
                  </>
                )}
              </fieldset>
            )}
          </section>
          <section className="panel">
            <h2>
              {t("ধাপ অনুযায়ী প্রকাশিত পাঠ", "Published lessons by level")}
            </h2>
            <p>
              {t(
                "একই ধাপে টেনে বা ওপর/নিচ বোতামে সাজান। প্রত্যাহার সঙ্গে সঙ্গে নতুন অনুশীলন বন্ধ করে।",
                "Drag within a level or use the up/down buttons. Withdrawal blocks new practice immediately.",
              )}
            </p>
            <label className="form-field">
              {t("প্রত্যাহারের কারণ", "Withdrawal reason")}
              <textarea
                minLength={10}
                maxLength={1000}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </label>
            {[1, 2, 3, 4, 5].map((level) => (
              <div key={level}>
                <h3>
                  {t("ধাপ", "Level")} {level}
                </h3>
                {data.published
                  .filter((p) => p.level === level)
                  .map((p, i, list) => (
                    <div
                      key={p.id}
                      className="panel"
                      draggable={!busy}
                      onDragStart={() => setDragged(p.id.slice(7))}
                      onDragEnd={() => setDragged(null)}
                      onDragOver={(e) => e.preventDefault()}
                      onDrop={(e) => {
                        e.preventDefault();
                        if (dragged) void move(dragged, p.id.slice(7));
                        setDragged(null);
                      }}
                    >
                      <strong>{lang === "bn" ? p.title : p.title_en}</strong>{" "}
                      <button
                        type="button"
                        disabled={busy || i === 0}
                        aria-label={t("ওপরে নিন", "Move up")}
                        onClick={() => step(p.id.slice(7), -1)}
                      >
                        ↑
                      </button>{" "}
                      <button
                        type="button"
                        disabled={busy || i === list.length - 1}
                        aria-label={t("নিচে নিন", "Move down")}
                        onClick={() => step(p.id.slice(7), 1)}
                      >
                        ↓
                      </button>{" "}
                      <button
                        type="button"
                        disabled={busy}
                        onClick={() => action(() => open(p.revision))}
                      >
                        {t("সংস্করণ দেখুন", "View version")}
                      </button>{" "}
                      <button
                        type="button"
                        disabled={busy || reason.trim().length < 10}
                        onClick={() =>
                          action(() =>
                            api("/api/admin/reading-content/withdraw", {
                              method: "POST",
                              body: JSON.stringify({
                                expected_revision: data.state.revision,
                                lesson_id: p.id.slice(7),
                                reason,
                              }),
                            }),
                          )
                        }
                      >
                        {t("প্রত্যাহার করুন", "Withdraw")}
                      </button>
                    </div>
                  ))}
              </div>
            ))}
            {ordered
              .filter(
                (id) => !data.published.some((p) => p.id === "lesson:" + id),
              )
              .map((id) => (
                <p key={id}>
                  {id} ·{" "}
                  {t(
                    "বর্তমান অনুমোদন নেই; জনসাধারণ দেখতে পায় না।",
                    "Current approval unavailable; hidden from public.",
                  )}{" "}
                  <button
                    type="button"
                    disabled={busy || reason.trim().length < 10}
                    onClick={() =>
                      action(() =>
                        api("/api/admin/reading-content/withdraw", {
                          method: "POST",
                          body: JSON.stringify({
                            expected_revision: data.state.revision,
                            lesson_id: id,
                            reason,
                          }),
                        }),
                      )
                    }
                  >
                    {t("প্রত্যাহার", "Withdraw")}
                  </button>
                </p>
              ))}
          </section>
        </>
      )}
    </div>
  );
}
