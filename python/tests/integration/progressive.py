import json
import time

import requests


BASE_URL = "http://localhost:8080/api"


def wait_for_api():
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            if requests.get(f"{BASE_URL}/health", timeout=1).ok:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise AssertionError("manager did not become healthy")


def first_sse_event(url: str, last_event_id: str | None = None):
    headers = {"Last-Event-ID": last_event_id} if last_event_id else {}
    with requests.get(
        f"http://localhost:8080{url}",
        headers=headers,
        stream=True,
        timeout=(5, 30),
    ) as response:
        response.raise_for_status()
        event_id = None
        for raw_line in response.iter_lines(decode_unicode=True):
            if raw_line.startswith("id: "):
                event_id = raw_line[4:]
            if raw_line.startswith("data: "):
                return event_id, json.loads(raw_line[6:])
    raise AssertionError("caption stream closed before producing a cue")


def main():
    wait_for_api()
    response = requests.post(
        f"{BASE_URL}/video/",
        json={
            "url": "http://fixture/speech.mp4",
            "source_language": "en",
            "target_language": "fr",
        },
        timeout=10,
    )
    response.raise_for_status()
    created = response.json()

    first_id, first_cue = first_sse_event(created["caption_events_url"])
    assert first_cue["language"] == "fr"

    state = requests.get(
        f"{BASE_URL}/video/{created['video_id']}", timeout=5
    ).json()
    assert state["translated_through_ms"] >= 10_000
    assert state["status"] == "processing", "first cue was not progressive"

    range_response = requests.get(
        f"http://localhost:8080{created['media_url']}",
        headers={"Range": "bytes=0-1023"},
        timeout=10,
    )
    assert range_response.status_code == 206
    assert len(range_response.content) == 1024

    second_id, second_cue = first_sse_event(
        created["caption_events_url"], first_id
    )
    assert second_id != first_id
    assert second_cue["segment_id"] != first_cue["segment_id"]

    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        state = requests.get(
            f"{BASE_URL}/video/{created['video_id']}", timeout=5
        ).json()
        if state["status"] == "completed":
            break
        if state["job"].get("error"):
            raise AssertionError(state["job"]["error"])
        time.sleep(1)
    else:
        raise AssertionError("translation did not complete")

    captions = requests.get(
        f"http://localhost:8080{created['caption_url']}", timeout=10
    )
    captions.raise_for_status()
    assert captions.text.startswith("WEBVTT\n")
    assert first_cue["text"] in captions.text
    assert second_cue["text"] in captions.text
    print("progressive integration test passed")


if __name__ == "__main__":
    main()
