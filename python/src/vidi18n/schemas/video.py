from vidi18n.schemas.base import Data, subscribable


class Chunk(Data):
    """
    A chunk of data referenced in the
    """

    start: int
    """
    The starting position of the chunk, in milliseconds
    """

    duration: int
    """
    The duration of this chunk in milliseconds
    """

    @subscribable
    def complete(self) -> bool:
        """
        Whether this chunk is complete or not
        """
        return False

    @property
    def parent_id(self) -> str:
        """
        The parent chunkable
        """
        raise NotImplementedError()

    @property
    def index(self) -> int:
        """
        The index of this chunk
        """
        # our uid is data:video_uid/track_type/track_index/chunk_index
        return int(self.uid.split("/")[-1])


class Chunkable(Data):
    """
    Describes a stream in a video that's (usually) split into chunks.
    """
    source: str
    """
    The process that created this chunkable.
    This is the service name that 
    """

    language: str
    """
    The language code of this chunkable
    """

    bitrate: int
    """
    Bandwidth required in bits per second
    """

    chunks: list[Chunk]
    """
    List of all the chunks, including ones that are not downloaded yet.
    """

    @property
    def type(self):
        """
        The type of chunkable.
        """
        return self.uid.split(":")[-1]

    @property
    def video_id(self) -> str:
        """
        The parent video
        """
        return self.uid.split(":")[1]

    @property
    def init_file(self) -> str | None:
        """
        The path to the init file for this chunkable
        """
        return None

    @property
    def index(self) -> int:
        """
        The index of this chunk
        """
        return int(self.uid.split(":")[-1])


class CaptionTrack(Chunkable):
    language: str
    format: str


class AudioTrack(Chunkable):
    language: str
    codec: str


class VideoTrack(Chunkable):
    language: str


class Video(Data):
    """
    Returns the video details
    """

    @subscribable
    def url(self):
        """
        The video URL.
        When this changes, the video will be downloaded.
        """
        pass

    duration: int | None
    """
    The duration of the video, in milliseconds
    """

    chunk_length: int | None
    """
    The duration of chunks in the video, in milliseconds
    """

    title: str | None
    """
    The title of the video
    """

    video: list[VideoTrack] = []
    """
    List of all the video tracks.
    """

    audio: list[AudioTrack] = []
    """
    List of all the audio tracks.
    Starts off with one, then more are added as the video is translated.
    """

    captions: list[CaptionTrack] = []
    """
    List of all the caption tracks.
    """

    @property
    def mpd_path(self):
        """
        The path to the MPD file for this video
        """
        return f"{self.uid}/index.mpd"
