import json
import subprocess

from redis import Redis
from vidi18n.schemas.video import Video


def url_changed(redis: Redis, key: bytes, value: bytes):
    """
    So we got a new URL. Time to download the video.
    """
    print("URL changed", key, value)

    uid = Video.key_to_uid(key.decode())
    url = value.decode()


def get_info(url):
    command = ["yt-dlp", "--dump-json", url]
    result = subprocess.run(command, stdout=subprocess.PIPE)
    video_info = json.loads(result.stdout.decode("utf-8"))

    duration = video_info["duration"]
    formats = {
        format["format_id"]: {
            "url": format["url"],
            "width": format["width"],
            "height": format["height"],
        }
        for format in formats
    }

    video_info["formats"]

    return video_info
