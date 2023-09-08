from pydantic import BaseModel


class Message(BaseModel):
    """
    Base class for queue messages
    """

    @property
    def name(self):
        """
        Returns the name of the request.
        """
        return self.__class__.__name__

    def __repr__(self):
        """
        Returns a string representation of the request.
        """
        return f"{self.name}({self.dict()})"


class Request(Message):
    """
    Base class for queue requests
    """

    pass


class Response(Message):
    """
    Base class for queue responses
    """

    status: str
    """
    Status of a response
    """

