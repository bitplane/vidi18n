from vidi18n.schemas.base import Data


class Chunk(Data):
    """
    A chunk was updated
    """

    video_id: str
    """
    The parent video's id
    """
