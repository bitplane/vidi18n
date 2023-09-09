from datetime import datetime
from enum import Enum

from vidi18n.schemas.base import Data, subscribable


class JobType(str, Enum):
    """
    The types of jobs that can be run
    """

    DOWNLOAD = "download"
    """
    Download the video
    """


class Video(Data):
    """
    Returns the video details
    """

    # chunk_count: int
    # """
    # The number of chunks in the video
    # """

    # chunk_size: int
    # """
    # The chunk size, in milliseconds
    # """

    @subscribable
    def url(self):
        pass
