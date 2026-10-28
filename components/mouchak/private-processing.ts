import type { RunResult } from "./types";
export type PrivateApi = <T>(path: string, options?: RequestInit) => Promise<T>;
export type ProcessingJob = {
  id: string;
  module: string;
  state: "queued" | "running" | "succeeded" | "failed" | "cancelled";
  run_id: string | null;
  error: string | null;
  expires_at: number;
};

export async function uploadPrivateFile(
  api: PrivateApi,
  file: File,
  progress: (completed: number, total: number) => void,
) {
  if (file.size <= 0 || file.size > 10 * 1024 * 1024)
    throw Error("ফাইলের আকার ১ byte–১০ MB হতে হবে / File must be 1 byte–10 MB");
  const digest = await crypto.subtle.digest(
    "SHA-256",
    await file.arrayBuffer(),
  );
  const checksum = Array.from(new Uint8Array(digest), (b) =>
    b.toString(16).padStart(2, "0"),
  ).join("");
  const upload = await api<{ id: string; chunk_bytes: number }>(
    "/api/uploads",
    {
      method: "POST",
      body: JSON.stringify({ size: file.size, checksum, consent: true }),
    },
  );
  if (upload.chunk_bytes !== 1024 * 1024)
    throw Error(
      "Upload configuration unavailable / আপলোড সেবা পাওয়া যাচ্ছে না",
    );
  try {
    const count = Math.ceil(file.size / upload.chunk_bytes);
    for (let index = 0; index < count; index++) {
      await api(`/api/uploads/${upload.id}/parts/${index}`, {
        method: "PUT",
        headers: { "Content-Type": "application/octet-stream" },
        body: file.slice(
          index * upload.chunk_bytes,
          (index + 1) * upload.chunk_bytes,
        ),
      });
      progress(index + 1, count);
    }
    return await api<{ id: string; scan_state: string }>(
      `/api/uploads/${upload.id}/complete`,
      { method: "POST" },
    );
  } catch (error) {
    // Best effort discards staged chunks. Expiry cleanup handles a lost connection.
    await api(`/api/uploads/${upload.id}`, { method: "DELETE" }).catch(
      () => {},
    );
    throw error;
  }
}

function pause(signal: AbortSignal) {
  signal.throwIfAborted();
  return new Promise<void>((resolve, reject) => {
    const abort = () => {
      clearTimeout(timer);
      reject(signal.reason);
    };
    const timer = setTimeout(() => {
      signal.removeEventListener("abort", abort);
      resolve();
    }, 2000);
    signal.addEventListener("abort", abort, { once: true });
  });
}

export async function runQueued(
  api: PrivateApi,
  slug: string,
  payload: string,
  signal: AbortSignal,
  onState: (job: ProcessingJob) => void,
): Promise<RunResult> {
  signal.throwIfAborted();
  let job = await api<ProcessingJob>(`/api/tools/${slug}/jobs`, {
    method: "POST",
    body: payload,
    signal,
  });
  const deadline = Date.now() + 16 * 60 * 1000;
  while (true) {
    signal.throwIfAborted();
    onState(job);
    if (job.state === "succeeded") {
      if (!job.run_id)
        throw Error("Result was removed / ফলাফল মুছে ফেলা হয়েছে");
      const run = await api<{ id: string; output: RunResult }>(
        `/api/runs/${job.run_id}`,
        { signal },
      );
      return { ...run.output, id: run.id };
    }
    if (["failed", "cancelled"].includes(job.state))
      throw Error(job.error || "কাজটি বাতিল হয়েছে / Processing cancelled");
    if (Date.now() > deadline)
      throw Error(
        "এই session-এর কাজ পাতায় অবস্থা দেখুন / Check the session work page for status",
      );
    await pause(signal);
    job = await api<ProcessingJob>(`/api/jobs/${job.id}`, { signal });
  }
}
