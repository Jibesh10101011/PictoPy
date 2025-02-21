from pydantic import BaseModel,Field, field_validator
from typing import Optional
from pydantic_core.core_schema import ValidationInfo


class AlbumCreate(BaseModel) :
    name : str
    description : Optional[str] = None
    is_hidden : bool = False
    password : Optional[str] = None

    @field_validator("password")
    def check_password(cls,value,info:ValidationInfo) :
        if info.data.get("is_hidden") and not value:
            raise ValueError("Password is required for hidden albums")
        return value


class AlbumResponse(BaseModel) :
    success : bool
    message : str
    data : dict 


class ErrorResponse(BaseModel) :
    success: bool = False
    message: str
    error: str

