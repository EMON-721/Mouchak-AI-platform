"""Bounded private MP4 processing, isolated from the web process."""

import json, math, os, subprocess, sys, tempfile, threading
from pathlib import Path
from .domain import InputError
from .pose_runtime import ROOT, availability

MAX_BYTES = 10 * 1024 * 1024
SLOTS = threading.BoundedSemaphore(2)


def probe(path):
    try:
        r = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-protocol_whitelist",
                "file,pipe",
                "-select_streams",
                "v",
                "-read_intervals",
                "%+#601",
                "-show_entries",
                "format=duration,format_name:stream=codec_name,width,height,avg_frame_rate:frame=best_effort_timestamp_time",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            timeout=4,
            check=True,
        )
        if len(r.stdout) > 200000:
            raise ValueError("excessive metadata")
        meta = json.loads(r.stdout)
        streams = meta["streams"]
        if len(streams) != 1:
            raise ValueError("one video stream required")
        s = streams[0]
        w, h = int(s["width"]), int(s["height"])
        duration = float(meta["format"]["duration"])
        a, b = s["avg_frame_rate"].split("/")
        fps = int(a) / int(b)
        frames = meta.get("frames", [])
        if (
            min(w, h) < 64
            or max(w, h) > 1920
            or w * h > 1920 * 1080
            or not math.isfinite(duration)
            or not 0 < duration <= 10
            or not math.isfinite(fps)
            or not 1 <= fps <= 60
            or not 2 <= len(frames) <= 600
            or s["codec_name"] not in ["h264", "mpeg4"]
            or "mp4" not in meta["format"]["format_name"]
        ):
            raise ValueError("unsupported clip")
        times = [float(f["best_effort_timestamp_time"]) for f in frames]
        origin = times[0]
        times = [t - origin for t in times]
        if any(not math.isfinite(t) or t < 0 or t > 10.1 for t in times) or any(
            b <= a for a, b in zip(times, times[1:])
        ):
            raise ValueError("invalid timestamps")
        return {
            "width": w,
            "height": h,
            "duration_seconds": duration,
            "fps": fps,
            "timestamps": times,
        }
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        subprocess.SubprocessError,
        ZeroDivisionError,
    ):
        raise InputError(
            "Use one readable MP4, at most 10 seconds, 1080p and 60 fps / সর্বোচ্চ ১০ সেকেন্ড, 1080p, 60 fps-এর একটি MP4 দিন"
        )


def validate_upload(data):
    if len(data) > MAX_BYTES or len(data) < 16 or data[4:8] != b"ftyp":
        raise InputError("Invalid MP4 signature or excessive size")
    with tempfile.TemporaryDirectory(prefix="mouchak-probe-") as d:
        p = Path(d) / "clip.mp4"
        p.write_bytes(data)
        return probe(p)


def analyze(clips):
    if not availability()["experimental_enabled"]:
        raise InputError(
            "Pose unavailable: experimental opt-in and verified weights required; production validation pending"
        )
    if not 1 <= len(clips) <= 2 or any(len(c) > MAX_BYTES for c in clips):
        raise InputError("Choose one clip and, optionally, one reference clip")
    if not SLOTS.acquire(blocking=False):
        raise InputError(
            "Pose workers busy; retry later / pose worker ব্যস্ত; পরে চেষ্টা করুন"
        )
    try:
        with tempfile.TemporaryDirectory(prefix="mouchak-pose-") as d:
            paths = []
            for i, data in enumerate(clips):
                p = Path(d) / f"clip-{i}.mp4"
                p.write_bytes(data)
                paths.append(str(p))
            try:
                r = subprocess.run(
                    [sys.executable, "-m", "services.model_worker.pose_worker", *paths],
                    cwd=ROOT,
                    capture_output=True,
                    timeout=35,
                    env={
                        **os.environ,
                        "OPENBLAS_NUM_THREADS": "2",
                        "OMP_NUM_THREADS": "2",
                    },
                )
                if len(r.stdout) > 900000:
                    raise InputError("Pose output exceeds bounded result size")
                payload = json.loads(r.stdout)
                if r.returncode or "error" in payload:
                    raise InputError(payload.get("error", "Pose processing failed"))
                return payload
            except (OSError, ValueError, subprocess.SubprocessError):
                raise InputError(
                    "Pose processing failed or timed out / pose প্রক্রিয়াকরণ ব্যর্থ বা সময় শেষ"
                )
    finally:
        SLOTS.release()
