import hashlib
import shutil
import re
import os

CACHE_DIR = "/tmp/video_cache"


def get_cached(source_file: str, element: str):
    """
    Given a source file and an element, return the cached version if it exists.
    """
    cache_name = get_cache_name(source_file)
    cache_path = os.path.join(CACHE_DIR, cache_name, element)

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    if os.path.isfile(cache_path):
        with open(cache_path, "rb") as f:
            return f.read()

    return None


def set_cached(source_file: str, element: str, data: bytes):
    cache_name = get_cache_name(source_file)
    cache_dir = os.path.join(CACHE_DIR, cache_name)
    os.makedirs(cache_dir, exist_ok=True)

    temp_path = os.path.join(cache_dir, f"{element}.tmp")
    final_path = os.path.join(cache_dir, element)

    with open(temp_path, "wb") as f_temp:
        f_temp.write(data)

    shutil.move(temp_path, final_path)

