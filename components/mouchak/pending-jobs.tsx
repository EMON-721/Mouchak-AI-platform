"use client";
import { useEffect, useState } from "react";
import { useApp } from "./context";
import { tools } from "./catalogue";
import type { ProcessingJob } from "./private-processing";

export function PendingJobs({ onOpen }: { onOpen: (id: string) => void }) {
  const { api, user, t } = useApp();
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [error, setError] = useState("");
  const [changing, setChanging] = useState("");
  useEffect(() => {
    if (!user) return;
    let live = true;
    let timer: ReturnType<typeof setTimeout>;
    const controller = new AbortController();
    async function poll() {
      try {
        const rows = await api<ProcessingJob[]>("/api/jobs", {
          signal: controller.signal,
        });
        if (!live) return;
        setJobs(rows);
        setError("");
        if (rows.some((j) => ["queued", "running"].includes(j.state)))
          timer = setTimeout(poll, 3000);
      } catch (e) {
        if (live) setError((e as Error).message);
      }
    }
    void poll();
    return () => {
      live = false;
      clearTimeout(timer);
      controller.abort();
    };
  }, [api, user]);
  async function cancel(id: string) {
    setChanging(id);
    try {
      const row = await api<ProcessingJob>(`/api/jobs/${id}/cancel`, {
        method: "POST",
      });
      setJobs((previous) => previous.map((j) => (j.id === id ? row : j)));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setChanging("");
    }
  }
  if (!jobs.length && !error) return null;
  const labels = {
    queued: t("অপেক্ষায়", "Waiting"),
    running: t("প্রক্রিয়াকরণ চলছে", "Processing"),
    succeeded: t("সম্পন্ন", "Completed"),
    failed: t("সম্পন্ন হয়নি", "Could not complete"),
    cancelled: t("বাতিল", "Cancelled"),
  };
  return (
    <section
      className="panel"
      aria-label={t("জমা দেওয়া কাজ", "Submitted work")}
    >
      <h2>{t("জমা দেওয়া কাজ", "Submitted work")}</h2>
      <p>
        {t(
          "পৃষ্ঠা বন্ধ হলেও জমা দেওয়া কাজ চলতে পারে। এই session থাকলে ফলাফল এখানে পাবেন।",
          "Submitted work can continue after closing a page. Results remain available in this session.",
        )}
      </p>
      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}
      {jobs.slice(0, 10).map((j) => (
        <article className="grant-card" key={j.id}>
          <strong>
            {tools.find((tool) => tool.slug === j.module)?.name || j.module}
          </strong>
          <p>{labels[j.state]}</p>
          {j.error ? <p>{j.error}</p> : null}
          {j.state === "succeeded" && j.run_id ? (
            <button className="text-link" onClick={() => onOpen(j.run_id!)}>
              {t("ফলাফল খুলুন", "Open result")}
            </button>
          ) : null}
          {["queued", "running"].includes(j.state) ? (
            <button
              className="text-link"
              disabled={changing === j.id}
              onClick={() => cancel(j.id)}
            >
              {t("কাজ বাতিল করুন", "Cancel work")}
            </button>
          ) : null}
        </article>
      ))}
    </section>
  );
}
