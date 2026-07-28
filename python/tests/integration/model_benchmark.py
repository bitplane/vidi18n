import json
import os
import time
from uuid import uuid4

import requests


BASE_URL = "http://localhost:8080/api"
FIRST_CUE_LIMIT = float(os.environ.get("VIDI18N_FIRST_CUE_LIMIT", "20"))
RTF_LIMIT = float(os.environ.get("VIDI18N_RTF_LIMIT", "1"))
EXPECTED_DEVICE = os.environ.get("VIDI18N_EXPECTED_DEVICE", "cpu")


def wait_for_ready():
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            health = requests.get(f"{BASE_URL}/health", timeout=2).json()
            if health["status"] == "ok":
                return health
        except requests.RequestException:
            pass
        time.sleep(1)
    raise AssertionError("real-model workers did not become ready")


def main():
    health = wait_for_ready()
    started = time.monotonic()
    response = requests.post(
        f"{BASE_URL}/video/",
        json={
            "url": f"http://fixture/speech.mp4?benchmark={uuid4()}",
            "source_language": "en",
            "target_language": "fr",
        },
        timeout=10,
    )
    response.raise_for_status()
    created = response.json()
    first_cue_seconds = None

    deadline = started + 180
    while time.monotonic() < deadline:
        state = requests.get(
            f"{BASE_URL}/video/{created['video_id']}", timeout=5
        ).json()
        if first_cue_seconds is None and state["translated_through_ms"] > 0:
            first_cue_seconds = time.monotonic() - started
        if state["job"].get("error"):
            raise AssertionError(state["job"]["error"])
        if state["status"] == "completed":
            break
        time.sleep(0.25)
    else:
        raise AssertionError("real-model translation did not complete")

    elapsed = time.monotonic() - started
    duration = state["duration_ms"] / 1000
    realtime_factor = elapsed / duration
    processors = state["metrics"]["processors"]
    transcriber = next(item for item in processors if item["stage"] == "transcribe")
    translator = next(item for item in processors if item["stage"] == "translate")
    assert transcriber["engine"] == "faster-whisper"
    assert transcriber["model"] == "tiny.en"
    assert transcriber["device"] == EXPECTED_DEVICE
    assert translator["engine"] == "argostranslate"

    captions = requests.get(
        f"http://localhost:8080{created['caption_url']}", timeout=10
    )
    captions.raise_for_status()
    assert captions.text.count(" --> ") >= 2
    assert "Bonjour du segment" not in captions.text
    assert first_cue_seconds is not None
    assert first_cue_seconds <= FIRST_CUE_LIMIT
    assert realtime_factor < RTF_LIMIT
    metrics = state["metrics"]
    assert metrics["first_caption_latency_ms"] <= FIRST_CUE_LIMIT * 1000
    assert metrics["realtime_factor"] < RTF_LIMIT
    assert metrics["stages"]["transcribe"]["count"] == state["total_chunks"]
    assert metrics["stages"]["translate"]["count"] == state["total_chunks"]

    result = {
        "status": "passed",
        "device": EXPECTED_DEVICE,
        "first_caption_seconds": round(first_cue_seconds, 3),
        "completion_seconds": round(elapsed, 3),
        "media_duration_seconds": round(duration, 3),
        "realtime_factor": round(realtime_factor, 4),
        "processors": processors,
        "workers": health["workers"],
    }
    print(
        f"real model benchmark passed: first cue "
        f"{result['first_caption_seconds']}s, RTF {result['realtime_factor']}"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
