from vidi18n.schemas.base import Request, Response


class CreateVideoRequest(Request):
    """
    Requests the creation of a new video
    """

    url: str
    """
    The URL where this video lives.
    """


class CreateVideoResponse(Response):
    """
    The response to a CreateVideoRequest
    """

    id: str
    """
    The ID of the video
    """
