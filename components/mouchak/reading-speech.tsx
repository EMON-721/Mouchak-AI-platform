"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useApp } from "./context";

type Status = {
  experimental_enabled: boolean;
  production_enabled: boolean;
  child_recording_enabled: boolean;
  checkpoint: string;
};
type Transcript = {
  supported: boolean;
  text: string;
  message: string;
  words: { word: string; start_seconds: number; end_seconds: number }[];
  alignment?: {
    reference_index: number | null;
    reference_word: string;
    heard_word: string;
    state: string;
  }[];
};

export function ReadingSpeech({
  passageId,
  onReviewedText,
}: {
  passageId: string;
  onReviewedText: (text: string) => void;
}) {
  const { t, lang, api } = useApp();
  const [status, setStatus] = useState<Status | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [reviewed, setReviewed] = useState(false);
  const [result, setResult] = useState<Transcript | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const pending = useRef<AbortController | null>(null);
  useEffect(() => {
    const control = new AbortController();
    api<Status>("/api/reading/speech/status", { signal: control.signal })
      .then(setStatus)
      .catch((e: Error) => {
        if (!control.signal.aborted) setError(e.message);
      });
    return () => {
      control.abort();
      pending.current?.abort();
    };
  }, [api, lang]);
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!file || !consent || busy) return;
    setError("");
    setResult(null);
    setReviewed(false);
    if (file.size > 10 * 1024 * 1024) {
      setError(t("সর্বোচ্চ ১০ MiB WAV দিন।", "Use a WAV of at most 10 MiB."));
      return;
    }
    const body = new FormData();
    body.set("file", file);
    body.set("recording_subject", "self_adult");
    body.set("adult_processing_consent", "true");
    body.set("passage_id", passageId);
    const control = new AbortController();
    pending.current = control;
    const timer = setTimeout(() => control.abort(), 110_000);
    setBusy(true);
    try {
      const response = await api<Transcript>("/api/reading/speech/transcribe", {
        method: "POST",
        body,
        signal: control.signal,
      });
      if (!control.signal.aborted) setResult(response);
    } catch (e) {
      if (pending.current === control)
        setError(
          control.signal.aborted
            ? t(
                "সময় শেষ হয়েছে। হাতে লেখা অনুশীলন চালু আছে।",
                "Request timed out. Typed practice remains available.",
              )
            : (e as Error).message,
        );
    } finally {
      clearTimeout(timer);
      if (pending.current === control) {
        pending.current = null;
        setBusy(false);
      }
    }
  }
  const states: Record<string, string> = {
    detected: t("শোনা গেছে", "Detected"),
    not_detected: t("শনাক্ত হয়নি", "Not detected"),
    review_uncertain: t("নিজে যাচাই করুন", "Review uncertainty"),
    extra_heard: t("বাড়তি শোনা গেছে", "Extra heard"),
  };
  return (
    <section className="panel tool-form" aria-labelledby="reading-speech-title">
      <p className="eyebrow">
        {t(
          "পরীক্ষামূলক · নিজের প্রাপ্তবয়স্ক কণ্ঠ",
          "EXPERIMENTAL · ADULT SELF-RECORDING",
        )}
      </p>
      <h2 id="reading-speech-title">
        {t("পড়ে বলা বাংলা লেখা দেখুন", "Review your spoken Bengali")}
      </h2>
      <p>
        {t(
          "এই স্থানীয় পরীক্ষায় নিজের ১–৩০ সেকেন্ডের 16-bit PCM WAV দিন। শিশু বা অন্য কারও কণ্ঠ দেবেন না। কাঁচা কণ্ঠ বা transcript রাখা হয় না। যন্ত্রের ভুলকে উচ্চারণ বা পড়ার দক্ষতার নম্বর ভাববেন না।",
          "For this local experiment, use your own 1–30 second 16-bit PCM WAV. Do not upload a child or another person's voice. Raw voice and transcript are not retained. ASR mistakes are not pronunciation or reading-ability scores.",
        )}
      </p>
      {!status?.experimental_enabled ? (
        <p role="status">
          {t(
            "কণ্ঠ পরীক্ষা এখন চালু নেই। হাতে লেখা ও শব্দে ট্যাপ করার অনুশীলন চালু আছে।",
            "Speech processing is unavailable. Typed and tap-word practice remains available.",
          )}
        </p>
      ) : (
        <form onSubmit={submit}>
          <label className="form-field">
            {t(
              "নিজের PCM WAV (সর্বোচ্চ ১০ MiB)",
              "Your PCM WAV (maximum 10 MiB)",
            )}
            <input
              type="file"
              accept="audio/wav,.wav"
              disabled={busy}
              required
              onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setResult(null);
                setReviewed(false);
              }}
            />
          </label>
          <label className="consent">
            <input
              type="checkbox"
              checked={consent}
              disabled={busy}
              onChange={(e) => {
                setConsent(e.target.checked);
                setResult(null);
                setReviewed(false);
              }}
            />
            {t(
              "আমি প্রাপ্তবয়স্ক। এটি আমার নিজের কণ্ঠ এবং এই একবার প্রক্রিয়াকরণে সম্মতি দিচ্ছি।",
              "I am an adult. This is my own voice and I consent to this single processing request.",
            )}
          </label>
          <button
            className="button primary"
            type="submit"
            disabled={busy || !consent || !file}
          >
            {busy
              ? t("বাংলা শনাক্ত হচ্ছে…", "Transcribing Bengali…")
              : t("কণ্ঠ থেকে লেখা দেখুন", "Transcribe my recording")}
          </button>
        </form>
      )}
      {error ? (
        <p role="alert" className="error">
          {error}
        </p>
      ) : null}
      {result ? (
        <div aria-live="polite">
          <p>
            {lang === "bn"
              ? result.message.split(" / ")[0]
              : result.message.split(" / ").at(-1)}
          </p>
          {result.supported ? (
            <>
              <blockquote>{result.text}</blockquote>
              <details>
                <summary>
                  {t("শব্দের সময় ও অনিশ্চয়তা", "Word timing and uncertainty")}
                </summary>
                <ul>
                  {result.words.map((w, i) => (
                    <li key={i}>
                      {w.word} · {w.start_seconds.toFixed(2)}–
                      {w.end_seconds.toFixed(2)} {t("সেকেন্ড", "seconds")}
                    </li>
                  ))}
                </ul>
                {result.alignment ? (
                  <ul>
                    {result.alignment.map((row, i) => (
                      <li key={i}>
                        {row.reference_word || row.heard_word} ·{" "}
                        {states[row.state] || row.state}
                        {row.state === "review_uncertain"
                          ? ` (${row.heard_word})`
                          : ""}
                      </li>
                    ))}
                  </ul>
                ) : null}
              </details>
              <label className="consent">
                <input
                  type="checkbox"
                  checked={reviewed}
                  onChange={(e) => setReviewed(e.target.checked)}
                />
                {t(
                  "লেখাটি নিজে যাচাই করেছি।",
                  "I have reviewed the transcript.",
                )}
              </label>
              <button
                className="button"
                type="button"
                disabled={!reviewed || !consent}
                onClick={() => onReviewedText(result.text)}
              >
                {t(
                  "যাচাই করা লেখা অনুশীলনের ঘরে নিন",
                  "Use reviewed text in the practice field",
                )}
              </button>
              <p className="subtle">
                {t(
                  "এতে ফলাফল সংরক্ষণ হয় না। নিচের অনুশীলন চালাতে আলাদা সম্মতি প্রয়োজন।",
                  "This does not save a result. The practice form below still needs its own processing consent.",
                )}
              </p>
            </>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}

type Lab = {
  runtime: Status;
  policy: { revision: string | null; state: string; reason: string };
  evaluation: {
    clips: number;
    speaker_groups: number;
    aggregate: { wer: number; cer: number; grapheme_error_rate: number };
    limitations: string[];
  } | null;
};
export function ReadingSpeechLab() {
  const { api, t } = useApp();
  const [data, setData] = useState<Lab | null>(null),
    [error, setError] = useState(""),
    [reason, setReason] = useState(""),
    [busy, setBusy] = useState(false);
  useEffect(() => {
    const c = new AbortController();
    api<Lab>("/api/admin/reading-speech", { signal: c.signal })
      .then(setData)
      .catch((e: Error) => {
        if (!c.signal.aborted) setError(e.message);
      });
    return () => c.abort();
  }, [api]);
  async function change(e: FormEvent) {
    e.preventDefault();
    if (!data || busy) return;
    setBusy(true);
    setError("");
    try {
      await api("/api/admin/reading-speech/policy", {
        method: "POST",
        body: JSON.stringify({
          state: data.policy.state === "disabled" ? "experimental" : "disabled",
          expected_revision: data.policy.revision,
          reason,
        }),
      });
      setData(await api<Lab>("/api/admin/reading-speech"));
      setReason("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel tool-form">
      <h1>{t("বাংলা speech lab", "Bengali speech lab")}</h1>
      <p>
        {t(
          "Model operator ও সাম্প্রতিক MFA প্রয়োজন। শিশু ও production gate এই পর্দা থেকে খোলা যায় না। ব্যক্তিগত recording-এর তালিকা নেই।",
          "Requires a model operator and recent MFA. Child and production gates cannot be opened here. No private recording list is exposed.",
        )}
      </p>
      {error ? (
        <p role="alert" className="error">
          {error}
        </p>
      ) : null}
      {data ? (
        <>
          <p>{data.runtime.checkpoint}</p>
          <p>
            {t("স্থানীয় পরীক্ষা", "Local experiment")}:{" "}
            {data.runtime.experimental_enabled
              ? t("চালু", "enabled")
              : t("বন্ধ", "disabled")}
          </p>
          {data.evaluation ? (
            <>
              <h2>
                {t(
                  "বাস্তবে মাপা সীমিত benchmark",
                  "Measured limited benchmark",
                )}
              </h2>
              <p>
                {data.evaluation.clips} {t("clip", "clips")} ·{" "}
                {data.evaluation.speaker_groups}{" "}
                {t("source speaker group", "source speaker groups")}
              </p>
              <dl>
                {Object.entries(data.evaluation.aggregate)
                  .filter(([k]) =>
                    ["wer", "cer", "grapheme_error_rate"].includes(k),
                  )
                  .map(([k, v]) => (
                    <div key={k}>
                      <dt>{k}</dt>
                      <dd>{(v * 100).toFixed(2)}%</dd>
                    </div>
                  ))}
              </dl>
              <p>
                {t(
                  "এটি শিশু, guardian বা বাংলাদেশের মাঠপর্যায়ের গ্রহণযোগ্যতা যাচাই নয়।",
                  "This is not child, guardian or Bangladesh field acceptance validation.",
                )}
              </p>
              <ul>
                {data.evaluation.limitations.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </>
          ) : (
            <p>
              {t(
                "এই checkpoint-এর মূল্যায়ন পাওয়া যায়নি।",
                "No evaluation for this checkpoint is available.",
              )}
            </p>
          )}
          <form onSubmit={change}>
            <label className="form-field">
              {t("পরিবর্তনের কারণ", "Reason for change")}
              <textarea
                value={reason}
                minLength={10}
                maxLength={1000}
                required
                disabled={busy}
                onChange={(e) => setReason(e.target.value)}
              />
            </label>
            <button
              type="submit"
              className="button"
              disabled={busy || reason.trim().length < 10}
            >
              {data.policy.state === "disabled"
                ? t(
                    "স্থানীয় opt-in আবার অনুমোদন করুন",
                    "Restore local opt-in eligibility",
                  )
                : t("এই মডেল বন্ধ করুন", "Disable this model")}
            </button>
          </form>
        </>
      ) : null}
    </section>
  );
}
