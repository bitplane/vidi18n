import os
import hashlib
import re


def get_cache_name(url: str) -> str:
    """
    Given an URL, give a nice safe cache name for it.
    Removes the protocol, replaces special characters with underscores,
    and adds some of the hashed version of the file back on the end
    to avoid collisions.
    """
    path = url.split("://", maxsplit=1)[-1]

    m = hashlib.sha256()
    m.update(path.encode("utf-8"))
    hash_hex = m.hexdigest()[:6]

    safe_name = re.sub(r"[^\w]", "_", path)
    safe_name = re.sub("_+", "_", safe_name)
    truncated_name = safe_name[:50]
    cache_name = f"{truncated_name}_{hash_hex}"

    return cache_name
