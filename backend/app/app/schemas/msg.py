from pydantic import BaseModel


class Msg(BaseModel):
    msg: str


class ErrorMsg(BaseModel):
    detail: str
