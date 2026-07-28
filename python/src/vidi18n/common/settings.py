import os


DATA_ROOT = os.environ.get("VIDI18N_DATA_ROOT", "/tmp/vidi18n")
PROCESSOR_MODE = os.environ.get("VIDI18N_PROCESSOR_MODE", "deterministic")
CHUNK_SECONDS = int(os.environ.get("VIDI18N_CHUNK_SECONDS", "10"))
MAX_ATTEMPTS = int(os.environ.get("VIDI18N_MAX_ATTEMPTS", "3"))

STREAM_DOWNLOAD = "vidi18n:work:download"
STREAM_TRANSCRIBE = "vidi18n:work:transcribe"
STREAM_TRANSLATE = "vidi18n:work:translate"
STREAM_PACKAGE = "vidi18n:work:package"


def video_key(video_id: str) -> str:
    return f"vidi18n:video:{video_id}"


def job_key(job_id: str) -> str:
    return f"vidi18n:job:{job_id}"


def caption_stream(video_id: str, language: str) -> str:
    return f"vidi18n:captions:{video_id}:{language}"


def metrics_key(job_id: str) -> str:
    return f"vidi18n:metrics:{job_id}"


def worker_key(worker: str) -> str:
    return f"vidi18n:worker:{worker}:ready"
