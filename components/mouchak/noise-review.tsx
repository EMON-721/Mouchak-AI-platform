"use client";
import { useApp } from "./context";
import type { RunResult } from "./types";
type Tag = {
  class_id: string;
  label_bn: string;
  label_en: string;
  uncalibrated_mean_score: number;
};
type Timeline = {
  start_seconds: number;
  end_seconds: number;
  label_bn: string;
  label_en: string;
  uncalibrated_score: number;
};
export function NoiseReview({ result }: { result: RunResult }) {
  const { t } = useApp();
  const tags = (result.facts.event_tags || []) as Tag[];
  const details = result.details as {
    waveform_rms?: number[];
    timeline?: Timeline[];
    inference_windows?: number;
  };
  const values = details.waveform_rms || [];
  const maximum = Math.max(...values, 0.000001);
  return (
    <section className="noise-studio">
      <p className="notice">
        {t(
          "পরীক্ষামূলক general-audio model। স্কোর calibrated probability, আইনি dB বা কারও পরিচয়ের প্রমাণ নয়। মূল class taxonomy ইংরেজিতে; অনুবাদ না থাকলে original label দেখানো হয়।",
          "Experimental general-audio model. Scores are not calibrated probabilities, legal dB measurements or identity evidence. The original taxonomy is English; untranslated labels retain their source names.",
        )}
      </p>
      <h3>{t("রেকর্ডিংয়ের আপেক্ষিক signal", "Relative recording signal")}</h3>
      <svg
        viewBox="0 0 640 110"
        role="img"
        aria-label={t(
          "সময় অনুযায়ী আপেক্ষিক RMS; dB নয়",
          "Relative RMS over time; not decibels",
        )}
      >
        {values.map((value, i) => (
          <rect
            key={i}
            x={i * 8}
            y={55 - (value / maximum) * 48}
            width={5}
            height={Math.max(1, (value / maximum) * 96)}
            fill="currentColor"
          />
        ))}
      </svg>
      <h3>
        {result.facts.supported
          ? t(
              "নিজে যাচাই করার জন্য সম্ভাব্য শব্দের ধরন",
              "Candidate sound tags to review",
            )
          : t("যথেষ্ট প্রমাণ পাওয়া যায়নি", "Insufficient evidence")}
      </h3>
      {tags.length ? (
        <div className="table-scroll">
          <table>
            <caption className="sr-only">
              {t(
                "মডেলের শব্দ tag ও uncalibrated score",
                "Model sound tags and uncalibrated scores",
              )}
            </caption>
            <thead>
              <tr>
                <th scope="col">{t("শব্দের ধরন", "Sound tag")}</th>
                <th scope="col">
                  {t("Uncalibrated score", "Uncalibrated score")}
                </th>
              </tr>
            </thead>
            <tbody>
              {tags.map((tag) => (
                <tr key={tag.class_id}>
                  <th scope="row">
                    {t(tag.label_bn, tag.label_en)}
                    <small>{tag.class_id}</small>
                  </th>
                  <td>{tag.uncalibrated_mean_score.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>
          {t(
            "নীরব, clipped বা অনির্ভরযোগ্য recording থেকে event label গ্রহণ করা হয়নি।",
            "No event label was accepted from silent, clipped or unreliable audio.",
          )}
        </p>
      )}
      {(details.timeline || []).length ? (
        <details>
          <summary>
            {t("সময় অনুযায়ী মডেলের tag দেখুন", "Inspect model tags over time")}
          </summary>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th scope="col">{t("সময় (সেকেন্ড)", "Time (seconds)")}</th>
                  <th scope="col">{t("পর্যালোচনার tag", "Tag to review")}</th>
                </tr>
              </thead>
              <tbody>
                {details.timeline?.map((frame, i) => (
                  <tr key={i}>
                    <td>
                      {frame.start_seconds.toFixed(2)}–
                      {frame.end_seconds.toFixed(2)}
                    </td>
                    <td>{t(frame.label_bn, frame.label_en)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      ) : null}
      <p className="subtle">
        {t(
          "আপনার রেকর্ডিং shared training corpus-এ যায়নি। বাংলাদেশি field evaluation এখনও বাকি।",
          "Your recording was not added to shared training. Bangladesh field evaluation remains incomplete.",
        )}
      </p>
    </section>
  );
}
