"""Real CPU worker: decoded timestamps, body landmarks and 2D joint angles."""

import json, sys
import numpy as np
from .domain import InputError, result
from .pose_runtime import PoseRuntime, MODEL_ID, ASSETS, features
from .pose_video import probe


def clip(runtime, path):
    import cv2

    meta = probe(path)
    cap = cv2.VideoCapture(str(path))
    frames = []
    next_time = 0.0
    try:
        for timestamp in meta["timestamps"]:
            ok, image = cap.read()
            if not ok:
                raise InputError("Video frame decoding incomplete; no result saved")
            if timestamp + 1e-6 < next_time:
                continue
            if image.shape[1] != meta["width"] or image.shape[0] != meta["height"]:
                raise InputError("Video dimensions change within the clip")
            scale = min(1, 1280 / image.shape[1], 720 / image.shape[0])
            if scale < 1:
                image = cv2.resize(
                    image, (int(image.shape[1] * scale), int(image.shape[0] * scale))
                )
            found = runtime.infer(image)
            found["timestamp_seconds"] = round(timestamp, 6)
            found["features"] = (
                features(found, image.shape[1], image.shape[0])
                if found["status"] == "tracked"
                else {}
            )
            frames.append(found)
            next_time = timestamp + 0.25
            if len(frames) >= 40:
                break
    finally:
        cap.release()
    tracked = [f for f in frames if f["status"] == "tracked"]
    summary = {}
    for key in [
        "left_knee_degrees",
        "right_knee_degrees",
        "left_elbow_degrees",
        "right_elbow_degrees",
    ]:
        values = [
            f["features"][key] for f in tracked if f["features"].get(key) is not None
        ]
        summary[key] = (
            {"minimum": min(values), "maximum": max(values), "samples": len(values)}
            if values
            else None
        )
    return {
        "frames": frames,
        "sampled_frames": len(frames),
        "tracked_frames": len(tracked),
        "valid_frame_percentage": round(100 * len(tracked) / max(1, len(frames)), 2),
        "duration_seconds": round(meta["duration_seconds"], 4),
        "width": meta["width"],
        "height": meta["height"],
        "summary": summary,
        "frame_timestamp_source": "decoded best_effort_timestamp_time",
        "raw_frames_returned": False,
    }


def compare(a, b):
    differences = {}
    for key in [
        "left_knee_degrees",
        "right_knee_degrees",
        "left_elbow_degrees",
        "right_elbow_degrees",
    ]:
        series = []
        for c in [a, b]:
            rows = [
                (f["timestamp_seconds"], f["features"].get(key))
                for f in c["frames"]
                if f["features"].get(key) is not None
            ]
            if len(rows) < 3 or rows[-1][0] <= rows[0][0]:
                return {
                    "comparable": False,
                    "reason": "Insufficient visible angle samples; no difference score",
                }
            t, v = np.array(rows).T
            series.append(
                np.interp(np.linspace(0, 1, 20), (t - t[0]) / (t[-1] - t[0]), v)
            )
        differences[key] = round(float(np.mean(np.abs(series[0] - series[1]))), 2)
    return {
        "comparable": True,
        "mean_absolute_angle_difference_degrees": differences,
        "alignment": "normalized clip time; not automatic stroke-phase alignment",
        "skill_score": None,
    }


def run(paths):
    runtime = PoseRuntime()
    clips = [clip(runtime, p) for p in paths]
    primary = clips[0]
    enough = primary["tracked_frames"] >= 3 and primary["valid_frame_percentage"] >= 60
    facts = {
        "pose_evidence_available": enough,
        "sampled_frames": primary["sampled_frames"],
        "tracked_frames": primary["tracked_frames"],
        "valid_frame_percentage": primary["valid_frame_percentage"],
        "duration_seconds": primary["duration_seconds"],
        "angle_ranges_2d": primary["summary"] if enough else None,
        "coaching_suggestions_validated": False,
    }
    output = result(
        "Real MediaPipe/BlazePose ONNX CPU; time-indexed 2D pose observations",
        facts,
        {
            "clips": clips,
            "comparison": compare(*clips) if len(clips) == 2 and enough else None,
            "checkpoint_checksums": ASSETS,
            "raw_video_or_faces_in_report": False,
        },
        [
            "Experimental only. Bangladesh phone-angle holdout and coach-reviewed suggestions have not passed. / পরীক্ষামূলক। বাংলাদেশের ফোনের কোণভিত্তিক পরীক্ষা ও coach-এর পরামর্শ যাচাই হয়নি।",
            "2D angles depend on camera position; no skill, injury, elite-performance or physical 3D assessment. / 2D কোণ camera-র উপর নির্ভর করে; দক্ষতা, injury বা প্রকৃত 3D মূল্যায়ন নয়।",
            "Blank, multiple-detection and low-confidence frames abstain. No validated practice drill recommendation. / ফাঁকা, একাধিক মানুষ ধরা পড়া বা কম নির্ভরতার frame-এ বিরত থাকে; যাচাইকৃত drill পরামর্শ নেই।",
        ],
    )
    output["status"] = "experimental_observation" if enough else "evidence_insufficient"
    output["model_version"] = MODEL_ID
    output["references"] = [
        {
            "title": "OpenCV Zoo MediaPipe Pose",
            "url": "https://github.com/opencv/opencv_zoo/tree/48b10fa505aeb51fbd127fc60a5c660040e823b7/models/pose_estimation_mediapipe",
            "license": "Apache-2.0",
            "kind": "model_provenance",
            "official": False,
        }
    ]
    return output


def main():
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024, 16 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    try:
        if not 1 <= len(sys.argv[1:]) <= 2:
            raise InputError("One or two clips required")
        print(json.dumps(run(sys.argv[1:]), ensure_ascii=False, allow_nan=False))
    except InputError as e:
        print(json.dumps({"error": str(e)}))
        return 1
    except Exception:
        print(
            json.dumps(
                {"error": "Pose inference failed; no prediction was substituted"}
            )
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
