from pydantic import BaseModel


class GetVideoByUrlRequest(BaseModel):
    """
    Given a URL, returns the video details.
    """

    url: str
    """
    The input URL
    """
