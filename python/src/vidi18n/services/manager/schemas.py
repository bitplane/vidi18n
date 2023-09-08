from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ProcessingStep(str, Enum):
    """
    The types of processing that the video can go through.
    """

    CREATE = "create"
    """
    Creating the MPD file and adding a reference to the video in the databse.
    """

    DOWNLOAD = "download"
    """
    Downloading from source and chunking.
    """

    TRANSCRIBE_AUDIO = "transcribe_audio"
    """

    """

    TRANSLATE_AUDIO = "translate_audio"
    """
    Machine translation
    """


class ProcessingStatus(BaseModel):
    """
    The status of a processing step.
    """

    updated: datetime
    """
    When this status was last updated.
    """

    success: int
    """
    The number of chunks that have completed processing.
    """

    error: bool
    """
    True if this step has errored
    """


class GetVideoByUrlRequest(BaseModel):
    """
    Given a URL, returns the video details.
    """

    url: str
    """
    The input URL
    """


class GetVideoByIdRequest(BaseModel):
    """
    Given a video ID, returns the path to the MPD file and stats
    """

    id: str
    """
    The video ID
    """


class VideoDetails(BaseModel):
    """
    Returns the video details
    """

    id: str
    """
    The ID of the video. This is the same as the path to the manifest file.
    """

    status_updated: datetime
    """
    The last time the video's status was updated
    """

    chunk_count: int
    """
    The number of chunks in the video
    """

    chunk_size: int
    """
    The chunk size, in milliseconds
    """

    status: dict[ProcessingStep, ProcessingStatus]
    """
    The status of each processing step
    """

    @property
    def is_complete(self) -> bool:
        """
        True if the video has completed processing
        """
        return all(
            [status.success == self.chunk_count for status in self.status.values()]
        )

    @property
    def is_error(self) -> bool:
        """
        Returns True if the video has errored
        """
        return any([status.error for status in self.status.values()])
