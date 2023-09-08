from vidi18n.schemas.base import Response


class ChunkUpdateResponse(Response):
    """
    A chunk was updated
    """

    video_id: str
    """
    The parent video's id
    """
    
    id: int
    """
    The index of the chunk
    """
