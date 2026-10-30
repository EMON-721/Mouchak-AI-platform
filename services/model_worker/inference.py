"""Real local inference. Absence of assets is an explicit unavailable state."""

from pathlib import Path
from functools import lru_cache
import os, json, re, subprocess, tempfile, time, hashlib, wave
import numpy as np
from PIL import Image
from .domain import InputError, result

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = Path(os.getenv("MODEL_DIR", ROOT / "models"))


def model_health():
    from .pose_runtime import availability
    from . import noise_runtime, reading_speech

    return {
        "pose": availability(),
        "noise_events": noise_runtime.availability(),
        "reading_asr": reading_speech.availability(),
        "ocr": {
            "runtime": "Tesseract",
            "ben_loaded": (MODEL_DIR / "ben.traineddata").is_file(),
            "eng_loaded": Path(
                "/usr/share/tesseract-ocr/5/tessdata/eng.traineddata"
            ).is_file(),
            "evaluated_for_production": False,
        },
        "embedding": {
            "checkpoint": "Xenova/paraphrase-multilingual-MiniLM-L12-v2 (quantized ONNX)",
            "weights_present": (MODEL_DIR / "minilm/model_quantized.onnx").is_file(),
            "evaluated_for_production": False,
        },
        "speech": {
            "status": (
                "experimental"
                if (MODEL_DIR / "whisper-tiny/model.bin").exists()
                else "unavailable"
            ),
            "checkpoint": "Systran/faster-whisper-tiny",
            "production_enabled": False,
            "reason": "Bangla holdout evaluation has not passed",
        },
        "vision_classifiers": {
            "status": "unavailable",
            "reason": "No locally labelled Bangladesh holdout is approved",
        },
    }


@lru_cache(maxsize=1)
def encoder():
    import onnxruntime as ort

    ort.disable_telemetry_events()
    from tokenizers import Tokenizer

    path = MODEL_DIR / "minilm/model_quantized.onnx"
    if not path.exists():
        raise InputError("Sentence embedding model unavailable / এমবেডিং মডেল নেই")
    t = Tokenizer.from_file(str(MODEL_DIR / "minilm/tokenizer.json"))
    t.enable_padding()
    t.enable_truncation(max_length=256)
    opt = ort.SessionOptions()
    opt.intra_op_num_threads = 2
    session = ort.InferenceSession(
        str(path), sess_options=opt, providers=["CPUExecutionProvider"]
    )
    return t, session


def embed(texts):
    t, s = encoder()
    encoded = t.encode_batch(texts)
    ids = np.array([x.ids for x in encoded], dtype=np.int64)
    mask = np.array([x.attention_mask for x in encoded], dtype=np.int64)
    types = np.array([x.type_ids for x in encoded], dtype=np.int64)
    args = {"input_ids": ids, "attention_mask": mask, "token_type_ids": types}
    out = s.run(None, {i.name: args[i.name] for i in s.get_inputs()})[0]
    if out.ndim == 3:
        weights = mask[..., None]
        out = (out * weights).sum(1) / np.maximum(weights.sum(1), 1)
    out = out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-12)
    if not np.isfinite(out).all():
        raise InputError("Embedding returned non-finite values")
    return out


@lru_cache(maxsize=1)
def corpus():
    docs = json.loads((ROOT / "data/authored/learning.json").read_text())
    vec = embed([x["title"] + " " + x["text_bn"] + " " + x["text_en"] for x in docs])
    return docs, vec


STOP_WORDS = set(
    "the what is a an who won of in to and how does do for from on with this that my your কী কি কাকে কেন কিভাবে কীভাবে এর ও এবং আমার কত করুন একটি এই সেই".split()
)


def tokens(s):
    return [
        x
        for x in re.findall(r"[\w\u0980-\u09ff]+", s.casefold())
        if x not in STOP_WORDS and not x.isdigit()
    ]


def retrieve(question, grade=None, lang="bn"):
    from rank_bm25 import BM25Okapi

    start = time.perf_counter()
    docs, vec = corpus()
    q = embed([question])[0]
    sem = vec @ q
    lex = BM25Okapi(
        [tokens(x["text_bn"] + " " + x["text_en"] + " " + x["title"]) for x in docs]
    )
    lexscores = lex.get_scores(tokens(question))
    order = sorted(
        range(len(docs)),
        key=lambda i: float(sem[i]) + 0.12 * float(lexscores[i]),
        reverse=True,
    )
    filtered = [i for i in order if not grade or docs[i]["grade"] == str(grade)]
    if not filtered:
        raise InputError(
            "No matching grade in the original starter corpus / এই শ্রেণির অনুমোদিত লেখা নেই"
        )
    i = filtered[0]
    supported = float(sem[i]) > 0.12 and float(lexscores[i]) > 0.01
    if not supported:
        r = result(
            "Real multilingual MiniLM + BM25, evidence refusal",
            {
                "supported": False,
                "answer": (
                    "এই প্রশ্নের সমর্থনে অনুমোদিত উৎস পাইনি।"
                    if lang == "bn"
                    else "No approved passage supports this question."
                ),
            },
            warnings=[
                "Only five original starter passages are available. No NCTB corpus was ingested."
            ],
        )
    else:
        d = docs[i]
        r = result(
            "Real multilingual MiniLM + BM25; extractive grounded answer",
            {
                "supported": True,
                "answer": d["text_bn"] if lang == "bn" else d["text_en"],
            },
            {
                "retrieval_similarity": round(float(sem[i]), 5),
                "lexical_score": round(float(lexscores[i]), 5),
                "corpus_documents": len(docs),
            },
            [
                "Original starter material, not an official textbook. Answer is an exact passage, not generated prose. / মৌলিক সহায়ক লেখা; সরকারি পাঠ্যবই নয়।"
            ],
        )
        r["references"] = [
            {
                k: d[k]
                for k in [
                    "id",
                    "title",
                    "license",
                    "publisher",
                    "source_date",
                    "official",
                ]
            }
        ]
    r["model_version"] = "Xenova/paraphrase-multilingual-MiniLM-L12-v2/ONNX-int8"
    r["latency_ms"] = round((time.perf_counter() - start) * 1000, 1)
    return r


def ocr(data, kind, page_number=None):
    from io import BytesIO

    pages = []
    if kind == "pdf":
        import pypdfium2 as pdfium

        pdf = pdfium.PdfDocument(data)
        if len(pdf) > 10:
            raise InputError("At most 10 PDF pages / সর্বোচ্চ ১০ পৃষ্ঠা")
        total_pages = len(pdf)
        if page_number is not None and not 1 <= page_number <= total_pages:
            raise InputError("Page does not exist / এই পৃষ্ঠা নেই")
        for index in ([page_number - 1] if page_number is not None else range(total_pages)):
            page = pdf[index]
            width, height = page.get_size()
            if width * height * 4 > 24000000:
                raise InputError("PDF page exceeds the image resolution limit")
            pages.append(page.render(scale=2).to_pil())
    else:
        im = Image.open(BytesIO(data))
        im.load()
        if page_number not in [None, 1]:
            raise InputError("Images have one page")
        total_pages = 1
        pages = [im.convert("RGB")]
    text_pages = []
    bn = (MODEL_DIR / "ben.traineddata").exists()
    with tempfile.TemporaryDirectory() as d:
        for idx, im in enumerate(pages):
            if im.width * im.height > 24000000:
                raise InputError("Image exceeds 24 megapixels / ছবির রেজোলিউশন বেশি")
            path = Path(d) / f"page-{idx}.png"
            im.save(path)
            args = [
                "tesseract",
                str(path),
                str(Path(d) / f"ocr-{idx}"),
                "-l",
                "ben+eng" if bn else "eng",
                "--psm",
                "6",
            ]
            if bn:
                args += ["--tessdata-dir", str(MODEL_DIR)]
            args += ["-c", "tessedit_create_tsv=1", "-c", "tessedit_create_txt=1"]
            try:
                subprocess.run(args, capture_output=True, text=True, timeout=45, check=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
                raise InputError("OCR failed or timed out / OCR ব্যর্থ বা সময় শেষ")
            import csv
            words = []
            with (Path(d) / f"ocr-{idx}.tsv").open() as tabular:
                for row in csv.DictReader(tabular, delimiter="\t", quoting=csv.QUOTE_NONE):
                    if row.get("level") != "5" or not row.get("text", "").strip():
                        continue
                    if len(words) >= 10000:
                        raise InputError("OCR word limit reached")
                    confidence = float(row["conf"])
                    words.append({"text": row["text"], "engine_word_confidence": confidence,
                                  "low_confidence_heuristic": confidence < 60,
                                  "x": int(row["left"]), "y": int(row["top"]),
                                  "width": int(row["width"]), "height": int(row["height"]),
                                  "line": f"{row['block_num']}:{row['par_num']}:{row['line_num']}"})
            text_pages.append({"page": page_number or idx + 1,
                               "text": (Path(d) / f"ocr-{idx}.txt").read_text().strip(),
                               "words": words, "image_width": im.width, "image_height": im.height})
    return {
        "pages": text_pages,
        "page_count": total_pages,
        "word_confidence_is_calibrated": False,
        "model": "Tesseract 5 ben+eng" if bn else "Tesseract 5 eng only",
        "human_confirmation_required": True,
        "confidence": "not calibrated; review all digits",
    }


def compare_images(data_a, data_b):
    import cv2

    a = cv2.imdecode(np.frombuffer(data_a, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    b = cv2.imdecode(np.frombuffer(data_b, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if a is None or b is None:
        raise InputError("Two readable images required / দুটি পড়া যায় এমন ছবি দিন")

    def shrink(x):
        h, w = x.shape
        return cv2.resize(
            x,
            (
                max(1, int(w * min(1, 1200 / max(h, w)))),
                max(1, int(h * min(1, 1200 / max(h, w)))),
            ),
        )

    a, b = shrink(a), shrink(b)
    orb = cv2.ORB_create(nfeatures=2500)
    ka, da = orb.detectAndCompute(a, None)
    kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None:
        raise InputError(
            "Insufficient visual features to align / ছবি মেলানোর মতো বৈশিষ্ট্য নেই"
        )
    matches = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(db, da, k=2)
    good = [
        x[0] for x in matches if len(x) == 2 and x[0].distance < 0.7 * x[1].distance
    ]
    if len(good) < 12:
        raise InputError(
            "Views cannot be reliably aligned / ছবির কোণ নির্ভরযোগ্যভাবে মেলেনি"
        )
    src = np.float32([kb[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([ka[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    h, inliers = cv2.findHomography(src, dst, cv2.RANSAC, 4)
    if h is None or inliers is None or int(inliers.sum()) < 10:
        raise InputError("Image alignment was unreliable / ছবি মেলানো নির্ভরযোগ্য হয়নি")
    aligned = cv2.warpPerspective(b, h, (a.shape[1], a.shape[0]))
    valid = cv2.warpPerspective(np.ones_like(b) * 255, h, (a.shape[1], a.shape[0])) > 0
    delta = np.abs(a.astype(np.float32) - aligned.astype(np.float32))[valid]
    return {
        "matched_features": len(good),
        "inlier_features": int(inliers.sum()),
        "mean_absolute_intensity_difference": round(float(delta.mean()), 3),
        "overlap_fraction": round(float(valid.mean()), 3),
        "erosion_or_water_extent_inferred": False,
    }


def audio_stats(data):
    from io import BytesIO

    try:
        with wave.open(BytesIO(data), "rb") as w:
            channels = w.getnchannels()
            rate = w.getframerate()
            width = w.getsampwidth()
            frames = w.getnframes()
            if width != 2 or frames / rate > 120:
                raise InputError(
                    "16-bit PCM WAV, at most 120 seconds / ১৬-বিট PCM WAV, সর্বোচ্চ ১২০ সেকেন্ড"
                )
            samples = (
                np.frombuffer(w.readframes(frames), dtype="<i2").astype(np.float64)
                / 32768
            )
    except (wave.Error, EOFError):
        raise InputError("Invalid PCM WAV / সঠিক PCM WAV নয়")
    if not samples.size:
        raise InputError("Empty recording / রেকর্ডিং খালি")
    return {
        "seconds": round(frames / rate, 3),
        "sample_rate": rate,
        "channels": channels,
        "rms_amplitude": round(float(np.sqrt(np.mean(samples**2))), 6),
        "peak_amplitude": round(float(np.max(np.abs(samples))), 6),
        "sound_class_inferred": False,
    }


@lru_cache(maxsize=1)
def speech_model():
    from faster_whisper import WhisperModel

    path = MODEL_DIR / "whisper-tiny"
    if not (path / "model.bin").exists():
        raise InputError(
            "Experimental speech checkpoint unavailable / পরীক্ষাধীন স্পিচ মডেল নেই"
        )
    return WhisperModel(
        str(path),
        device="cpu",
        compute_type="int8",
        cpu_threads=2,
        num_workers=1,
        local_files_only=True,
    )


def transcribe(data, language="bn"):
    """Experimental adult transcription. No pronunciation/medical inference."""
    from io import BytesIO

    if language not in ["bn", "en"]:
        raise InputError("Choose bn or en")
    started = time.perf_counter()
    try:
        decoded = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                "pipe:0",
                "-t",
                "121",
                "-f",
                "s16le",
                "-ac",
                "1",
                "-ar",
                "16000",
                "pipe:1",
            ],
            input=data,
            capture_output=True,
            check=True,
            timeout=30,
        ).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        raise InputError("Audio decoding failed / অডিও পড়া যায়নি")
    audio = np.frombuffer(decoded, dtype="<i2").astype(np.float32) / 32768
    if not audio.size or audio.size / 16000 > 120:
        raise InputError("Audio must be nonempty and at most 120 seconds")
    segments, info = speech_model().transcribe(
        audio,
        language=language,
        beam_size=3,
        vad_filter=True,
        condition_on_previous_text=False,
        no_speech_threshold=0.7,
    )
    if info.duration > 120:
        raise InputError("Audio must be at most 120 seconds / সর্বোচ্চ ১২০ সেকেন্ড")
    out = []
    for s in segments:
        if s.no_speech_prob > 0.7 or s.avg_logprob < -1:
            continue
        out.append(
            {
                "start": round(s.start, 2),
                "end": round(s.end, 2),
                "text": s.text.strip(),
                "average_log_probability": round(s.avg_logprob, 4),
            }
        )
    return {
        "status": "experimental",
        "model": "Systran/faster-whisper-tiny",
        "language": language,
        "duration_seconds": round(info.duration, 2),
        "segments": out,
        "text": " ".join(s["text"] for s in out),
        "latency_ms": round((time.perf_counter() - started) * 1000, 1),
        "bangla_accuracy_evaluated": False,
        "human_confirmation_required": True,
        "pronunciation_score": None,
    }


def personal_anomalies(values):
    """Fit only an explicitly supplied private baseline; never shared training."""
    from sklearn.ensemble import IsolationForest

    if len(values) < 25 or len(values) > 500:
        raise InputError(
            "Need 25–500 confirmed private measurements / ২৫–৫০০টি নিশ্চিত মাপ প্রয়োজন"
        )
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or not 1 <= array.shape[1] <= 8 or not np.isfinite(array).all():
        raise InputError("Invalid numeric baseline / সংখ্যাভিত্তিক তথ্য সঠিক নয়")
    model = IsolationForest(
        n_estimators=100, random_state=42, contamination="auto", n_jobs=1
    ).fit(array)
    scores = model.decision_function(array)
    return {
        "model": "sklearn.IsolationForest/random_state=42",
        "sample_size": len(values),
        "scores": [round(float(x), 6) for x in scores],
        "outlier_flags": [bool(x == -1) for x in model.predict(array)],
        "method": "Personal exploratory baseline; not calibrated for diagnosis or forecasting",
        "shared_training": False,
    }
