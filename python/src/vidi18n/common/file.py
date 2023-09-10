import os

import requests

MANAGER_ENDPOINT = os.environ.get("MANAGER_API", "http://localhost:8081")


def write(path: str, data: bytes):
    """
    Save file data to a file by posting to manager service's HTTP API
    """
    response = requests.put(f"{MANAGER_ENDPOINT}/files/{path}", data)

    return response.content


def read(path: str):
    """
    Read file data from manager service's HTTP API
    """
    response = requests.get(f"{MANAGER_ENDPOINT}/files/{path}")

    return response.content
