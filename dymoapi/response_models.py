from pydantic import BaseModel

class UrlEncryptResponse(BaseModel):
    original: str
    code: str
    encrypt: str