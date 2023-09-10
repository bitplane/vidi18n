import json
import subprocess


def get_info(url):
    command = ["yt-dlp", "--dump-json", url]
    result = subprocess.run(command, stdout=subprocess.PIPE)
    video_info = json.loads(result.stdout.decode("utf-8"))

    #    formats = {
    #        format["format_id"]: {
    #            "url": format["url"],
    #            "width": format["width"],
    #            "height": format["height"],
    #        }
    #        for format in formats
    #    }

    return video_info
