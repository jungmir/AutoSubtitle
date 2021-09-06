from fastapi import FastAPI, Form, UploadFile, Depends
from pydantic import BaseModel
import inspect
from typing import Optional, Type

app = FastAPI()


def as_form(cls: Type[BaseModel]):
    """
    Adds an as_form class method to decorated models. The as_form class method
    can be used with FastAPI endpoints
    """
    new_params = [
        inspect.Parameter(
            field.alias,
            inspect.Parameter.POSITIONAL_ONLY,
            default=(Form(field.default) if not field.required else Form(...)),
        )
        for field in cls.__fields__.values()
    ]

    async def _as_form(**data):
        return cls(**data)

    sig = inspect.signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig
    setattr(cls, "as_form", _as_form)
    return cls

@as_form
class Item(BaseModel):
    data_type : str
    url : str
    file: UploadFile
    callback : str
    video_type : Optional[str] = 'mp4'
    language : Optional[str] = 'en-US'
    window_size : Optional[float] = 0.5
    threshold : Optional[float] = 0.3

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def uploadFile(item:Item = Depends(Item.as_form)):
    return item