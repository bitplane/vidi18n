from redis import Redis
from vidi18n.schemas.video import Video
from vidi18n.services.download.yt_dl import get_info


def url_changed(redis: Redis, key: bytes, value: bytes):
    """
    So we got a new URL. Time to download the video.
    """
    print("URL changed", key, value)

    uid = Video.key_to_uid(key.decode())
    url = value.decode()

    video = Video.load(uid=uid)

    video_info = get_info(url)
