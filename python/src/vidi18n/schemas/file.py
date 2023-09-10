from pydantic import BaseModel


class File(BaseModel):
    """
    File data for synchronous calls
    """

    data: bytes
