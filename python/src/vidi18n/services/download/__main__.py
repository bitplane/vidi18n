from vidi18n.common.redis import get_redis, listen_for_events
from vidi18n.schemas.video import Video
from vidi18n.services.download.listeners import url_changed


def main():
    redis = get_redis()
    listen_for_events(redis, Video.field_key("url"), url_changed)


if __name__ == "__main__":
    main()
