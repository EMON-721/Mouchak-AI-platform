"""Checksum-pinned CPU BlazePose; Apache-2.0 OpenCV Zoo transforms, explicit ONNX output names."""

import hashlib, os
from pathlib import Path
import numpy as np
from .domain import InputError

ROOT = Path(__file__).resolve().parents[2]
ASSETS = {
    "person.onnx": "47fd5599d6fa17608f03e0eb0ae230baa6e597d7e8a2c8199fe00abea55a701f",
    "pose.onnx": "9d89c599319a18fb7d2e28451a883476164543182bafca5f09eb2cf767ed2f3f",
}
MODEL_ID = "opencv-zoo/mediapipe-pose@48b10fa505aeb51fbd127fc60a5c660040e823b7/onnx-cpu"


def model_dir():
    return Path(os.getenv("MODEL_DIR", ROOT / "models")) / "pose"


def verify_models():
    for name, expected in ASSETS.items():
        p = model_dir() / name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise InputError(
                "Pose model missing or checksum mismatch / pose মডেল নেই বা checksum মেলেনি"
            )
    return model_dir()


def availability():
    try:
        verify_models()
        installed = True
    except InputError:
        installed = False
    return {
        "checkpoint": MODEL_ID,
        "weights_verified": installed,
        "experimental_enabled": installed
        and os.getenv("ENABLE_EXPERIMENTAL_POSE") == "1"
        and os.getenv("MOUCHAK_ENV") != "production",
        "production_enabled": False,
        "evaluated_for_production": False,
        "reason": "Bangladesh phone-angle holdout and coach-reviewed suggestions are not validated",
    }


class PoseRuntime:
    def __init__(self):
        import cv2 as cv, onnxruntime as ort

        ort.disable_telemetry_events()
        from .vendor.opencv_zoo.mp_persondet import MPPersonDet
        from .vendor.opencv_zoo.mp_pose import MPPose

        path = verify_models()
        cv.setNumThreads(2)
        opt = ort.SessionOptions()
        opt.intra_op_num_threads = 2
        opt.inter_op_num_threads = 1
        self.detector_session = ort.InferenceSession(
            str(path / "person.onnx"),
            sess_options=opt,
            providers=["CPUExecutionProvider"],
        )
        self.pose_session = ort.InferenceSession(
            str(path / "pose.onnx"),
            sess_options=opt,
            providers=["CPUExecutionProvider"],
        )
        self.detector = MPPersonDet.__new__(MPPersonDet)
        self.detector.input_size = np.array([224, 224])
        self.detector.anchors = self.detector._load_anchors()
        self.detector.score_threshold = 0.6
        self.detector.nms_threshold = 0.3
        self.detector.topK = 20
        self.pose = MPPose.__new__(MPPose)
        self.pose.input_size = np.array([256, 256])
        self.pose.conf_threshold = 0.6
        self.pose.PERSON_BOX_PRE_ENLARGE_FACTOR = 1
        self.pose.PERSON_BOX_ENLARGE_FACTOR = 1.25

    def infer(self, image):
        h, w = image.shape[:2]
        if min(h, w) < 64 or h * w > 1280 * 720:
            raise InputError("Pose frame resolution outside supported range")
        blob, bias = self.detector._preprocess(image)
        # The pinned detector's regression tensor MUST precede its score tensor.
        outputs = self.detector_session.run(
            ["Identity:0", "Identity_1:0"], {"input_1:0": blob}
        )
        people = self.detector._postprocess(outputs, np.array([w, h]), bias)
        if len(people) != 1:
            return {
                "status": "no_person" if not len(people) else "multiple_people",
                "landmarks": [],
            }
        person = people[0]
        points = person[4:12].reshape(-1, 2)
        radius = float(np.linalg.norm(points[0] - points[1]))
        if not np.isfinite(person).all() or not 8 <= radius <= max(w, h) * 1.5:
            return {"status": "invalid_person_region", "landmarks": []}
        blob, box, angle, rotation, bias = self.pose._preprocess(image, person.copy())
        outputs = self.pose_session.run(
            ["Identity", "Identity_1", "Identity_2", "Identity_3", "Identity_4"],
            {"input_1": blob},
        )
        found = self.pose._postprocess(
            outputs, box, angle, rotation, bias, np.array([w, h])
        )
        if found is None:
            return {"status": "low_pose_confidence", "landmarks": []}
        raw = found[1][:33]
        if not np.isfinite(raw).all():
            return {"status": "invalid_landmarks", "landmarks": []}
        landmarks = [
            {
                "id": i,
                "x": round(float(p[0]) / w, 6),
                "y": round(float(p[1]) / h, 6),
                "visibility": round(float(p[3]), 5),
                "presence": round(float(p[4]), 5),
            }
            for i, p in enumerate(raw)
        ]
        valid = sum(
            p["visibility"] >= 0.6
            and p["presence"] >= 0.6
            and 0 <= p["x"] <= 1
            and 0 <= p["y"] <= 1
            for p in landmarks
        )
        return {
            "status": "tracked" if valid >= 20 else "insufficient_visible_landmarks",
            "landmarks": landmarks if valid >= 20 else [],
            "visible_landmark_count": valid,
            "pose_confidence": round(float(found[-1]), 5),
        }


def features(frame, width, height):
    """Descriptive 2D image-plane angles; no physical 3D or skill inference."""
    points = {
        p["id"]: p
        for p in frame["landmarks"]
        if p["visibility"] >= 0.6
        and p["presence"] >= 0.6
        and 0 <= p["x"] <= 1
        and 0 <= p["y"] <= 1
    }

    def angle(a, b, c):
        if not all(k in points for k in [a, b, c]):
            return None
        p = [
            np.array([points[k]["x"] * width, points[k]["y"] * height])
            for k in [a, b, c]
        ]
        left, right = p[0] - p[1], p[2] - p[1]
        norm = float(np.linalg.norm(left) * np.linalg.norm(right))
        return (
            None
            if norm < 1e-8
            else round(
                float(
                    np.degrees(np.arccos(np.clip(np.dot(left, right) / norm, -1, 1)))
                ),
                2,
            )
        )

    return {
        "left_knee_degrees": angle(23, 25, 27),
        "right_knee_degrees": angle(24, 26, 28),
        "left_elbow_degrees": angle(11, 13, 15),
        "right_elbow_degrees": angle(12, 14, 16),
    }
