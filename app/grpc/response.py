from pydantic import BaseModel


class GRPCResponse(BaseModel):
    message: str
    received: bool
