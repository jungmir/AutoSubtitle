from math import log
from fastapi import FastAPI, Form, UploadFile, File, Depends, Request
from fastapi.logger import logger
from pydantic import BaseModel
from typing import Optional, Type
from Downloader import Downloader
from ExtractAudio import Extract
import inspect, os, urllib, asyncio, threading

app = FastAPI()

progress_name = None
progress_status = 'wait'
progress_bar = 0


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

def get_youtube_video_id(url):
    return url.split('watch?v=')[-1]

async def extract_video(video_id, video_type, language, upload_callback_url):
    try:
        task = threading.Thread(target=Extract(
                video_id=video_id, 
                video_type=video_type, 
                language=language, 
                callback=upload_callback_url,
                temp_video_path='temp/videos'
        ).extract)
        await asyncio.wait(task.start())
    except Exception as e:
        return False
    return True

async def download_video(video_id, video_type, language, upload_callback_url):
    try:
        task = threading.Thread(target=Downloader().download, args=(video_id))
        await asyncio.wait(task.start())
        task = threading.Thread(target=Extract(
                video_id=video_id, 
                video_type=video_type, 
                language=language, 
                callback=upload_callback_url,
                temp_video_path='temp/videos'
        ).extract)
        await asyncio.wait(task.start())
    except Exception as e:
        return False
    return True

@as_form
class Item(BaseModel):
    data_type : str
    url : str
    file: UploadFile = File(...)
    video_type : Optional[str] = 'mp4'
    language : Optional[str] = 'en-US'
    window_size : Optional[float] = 0.5
    threshold : Optional[float] = 0.3

class Progress(BaseModel):
    task: str
    status: str
    progress: int

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload_file(request: Request, item: Item = Depends(Item.as_form)):
    video_id = ''

    if item.data_type == "url":
        # @TODO: split youtube video id
        video_id = get_youtube_video_id(item.url)

        # @TODO: download video file
        Downloader.download(video_id)
    elif item.data_type == 'file':
        # @TODO: save file
        video_id, _ = item.file.filename.split('.')
        temp_dir_path = os.path.join(os.path.dirname(__file__), f'temp/videos/{video_id}')
        file_name = os.path.join(temp_dir_path, item.file.filename)
        file_data = await item.file.read()
        with open(file_name, 'wb') as buffer:
            buffer.write(file_data)
            buffer.close()

    upload_callback_url = urllib.parse.urljoin(str(request.url), '/upload/status')

    # @TODO: extract audio
    loop = asyncio.get_running_loop()
    if loop and loop.is_running():
        tsk = loop.create_task(extract_video(video_id, item.video_type, item.language, upload_callback_url))
        # ^-- https://docs.python.org/3/library/asyncio-task.html#task-object
        tsk.add_done_callback(                                          # optional
            lambda t: print(f'Task done: '                              # optional
                            f'{t.result()=} << return val of main()'))  # optional (using py38)
    else:
        print('Starting new event loop')
        asyncio.run(extract_video(video_id, item.video_type, item.language, upload_callback_url))

    return item

@app.get('/upload/status')
async def check_upload_status():
    return {'task': progress_name, 'status': progress_status, 'progress': progress_bar}

@app.post('/upload/status')
async def set_upload_status(request: Request, progress_data: Progress):
    progress_name = progress_data.task
    progress_bar = progress_data.progress
    progress_status = progress_data.status
    logger.debug(f'{progress_name}/{progress_status}/{progress_bar}')
    return {'ok': True}