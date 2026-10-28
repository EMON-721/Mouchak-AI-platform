"use client";
import { useEffect, useState } from "react";
import { useApp } from "./context";
type Point = {
  id: number;
  x: number;
  y: number;
  visibility: number;
  presence: number;
};
type Frame = { timestamp_seconds: number; status: string; landmarks: Point[] };
type Clip = {
  frames: Frame[];
  width: number;
  height: number;
  valid_frame_percentage: number;
  summary: unknown;
};
type Detail = {
  clips: Clip[];
  comparison: unknown;
  checkpoint_checksums: unknown;
};
const edges = [
  [11, 12],
  [11, 13],
  [13, 15],
  [12, 14],
  [14, 16],
  [11, 23],
  [12, 24],
  [23, 24],
  [23, 25],
  [25, 27],
  [24, 26],
  [26, 28],
  [27, 29],
  [29, 31],
  [28, 30],
  [30, 32],
];
function parsed(value: unknown): Detail | null {
  if (!value || typeof value !== "object") return null;
  const d = value as Detail;
  return Array.isArray(d.clips) &&
    d.clips.length > 0 &&
    d.clips.length <= 2 &&
    d.clips.every(
      (c) =>
        Array.isArray(c.frames) &&
        c.frames.length <= 40 &&
        c.width > 0 &&
        c.height > 0,
    )
    ? d
    : null;
}
export function poseDetailSummary(value: unknown) {
  const d = parsed(value);
  return d
    ? {
        comparison: d.comparison,
        checkpoint_checksums: d.checkpoint_checksums,
        clips: d.clips.map((c) => ({
          valid_frame_percentage: c.valid_frame_percentage,
          sampled_frames: c.frames.length,
          angle_ranges_2d: c.summary,
        })),
      }
    : value;
}
export function PoseReview({ details }: { details: unknown }) {
  const { t } = useApp();
  const [index, setIndex] = useState(0),
    [playing, setPlaying] = useState(false),
    [speed, setSpeed] = useState(0.25);
  const data = parsed(details),
    clip = data?.clips[0],
    frames = clip?.frames || [],
    last = frames.length - 1;
  useEffect(() => {
    if (!playing || last < 1) return;
    const timer = setInterval(
      () => setIndex((i) => (i >= last ? 0 : i + 1)),
      250 / speed,
    );
    return () => clearInterval(timer);
  }, [playing, speed, last]);
  if (!data || !clip || !frames.length) return null;
  const active = frames[Math.min(index, last)],
    reference = data.clips[1];
  const second =
    reference?.frames[
      Math.round((index / Math.max(1, last)) * (reference.frames.length - 1))
    ];
  function skeleton(frame: Frame | undefined, color: string) {
    const points = new Map(
      (frame?.landmarks || [])
        .filter(
          (p) =>
            p.id >= 11 &&
            p.visibility >= 0.6 &&
            p.presence >= 0.6 &&
            p.x >= 0 &&
            p.x <= 1 &&
            p.y >= 0 &&
            p.y <= 1,
        )
        .map((p) => [p.id, p]),
    );
    return (
      <g
        stroke={color}
        strokeWidth={Math.max(2, clip!.width / 200)}
        fill={color}
      >
        {edges.map(([a, b]) =>
          points.has(a) && points.has(b) ? (
            <line
              key={`${a}:${b}`}
              x1={points.get(a)!.x * clip!.width}
              y1={points.get(a)!.y * clip!.height}
              x2={points.get(b)!.x * clip!.width}
              y2={points.get(b)!.y * clip!.height}
            />
          ) : null,
        )}
        {[...points.values()].map((p) => (
          <circle
            key={p.id}
            cx={p.x * clip!.width}
            cy={p.y * clip!.height}
            r={Math.max(3, clip!.width / 150)}
          />
        ))}
      </g>
    );
  }
  return (
    <section
      className="pose-review"
      aria-label={t("সময় অনুযায়ী pose দেখুন", "Review pose over time")}
    >
      <h3>
        {t("পরীক্ষামূলক pose পর্যবেক্ষণ", "Experimental pose observations")}
      </h3>
      <p>
        {t(
          "এখানে শুধু শরীরের landmark আঁকা হয়; মূল ভিডিও বা মুখ দেখানো হয় না। কোণ camera-র উপর নির্ভর করে। এটি skill score বা injury assessment নয়।",
          "Only body landmarks are drawn; the original video and face are not displayed. Angles depend on the camera. This is not a skill score or injury assessment.",
        )}
      </p>
      <svg
        role="img"
        aria-label={t(
          "নির্বাচিত frame-এর শরীরের landmark",
          "Body landmarks in the selected frame",
        )}
        viewBox={`0 0 ${clip.width} ${clip.height}`}
        style={{
          width: "100%",
          maxHeight: 440,
          background: "var(--paper, #f5f3ec)",
          borderRadius: 12,
        }}
      >
        {skeleton(second, "#bd7439")}
        {skeleton(active, "#147774")}
      </svg>
      <p role="status">
        {active.timestamp_seconds.toFixed(2)} s · {t("Frame", "Frame")}{" "}
        {index + 1}/{frames.length} ·{" "}
        {active.status === "tracked"
          ? t("pose পাওয়া গেছে", "pose tracked")
          : t(
              "এই frame-এ যথেষ্ট প্রমাণ নেই",
              "insufficient evidence in this frame",
            )}
      </p>
      {reference ? (
        <p>
          {t(
            "সবুজ: নিজের clip · কমলা: নির্বাচিত reference। Clip-এর সময় মিলিয়ে দেখানো; stroke phase স্বয়ংক্রিয়ভাবে মেলানো নয়।",
            "Teal: your clip · amber: selected reference. Aligned by clip time; stroke phases are not automatically matched.",
          )}
        </p>
      ) : null}
      <label>
        {t("Frame বেছে নিন", "Choose frame")}
        <input
          type="range"
          min={0}
          max={Math.max(0, last)}
          value={index}
          onChange={(e) => {
            setPlaying(false);
            setIndex(Number(e.target.value));
          }}
        />
      </label>
      <div className="row-actions">
        <button
          type="button"
          className="button outline"
          disabled={last < 1}
          aria-pressed={playing}
          onClick={() => setPlaying((p) => !p)}
        >
          {playing ? t("থামান", "Pause") : t("Pose replay", "Replay pose")}
        </button>
        <label>
          {t("গতি", "Speed")}
          <select
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
          >
            <option value={0.25}>0.25×</option>
            <option value={0.5}>0.5×</option>
            <option value={1}>1×</option>
          </select>
        </label>
      </div>
      <p>
        {t(
          "সম্পূর্ণ time-indexed landmarks JSON export-এ আছে। Coach review ও Bangladesh evaluation এখনো বাকি।",
          "Full time-indexed landmarks are in the JSON export. Coach review and Bangladesh evaluation are still pending.",
        )}
      </p>
    </section>
  );
}
