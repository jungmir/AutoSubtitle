from __future__ import unicode_literals
from youtube_dl import YoutubeDL, utils
from config import path
from pathlib import Path
from glob import glob

import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
SUB_LANG = sorted(['ko', 'en'])

def my_hook(data):
    if data['status'] == 'finished':
        logger.info('Done downloading, now converting ...')

class MyLogger(object):
    def debug(self, msg):
        logger.debug(msg)
    def warning(self, msg):
        logger.warning(msg)
    def error(self, msg):
        logger.error(msg)

class Downloader:
    def __init__(self, video_path = path.video_path, option={}):
        self._url = f'http://youtube.com/watch?v=%s'
        self._video_path = video_path
        self._option = {
                        'logger' : MyLogger(),
                        'progress_hooks': [my_hook],
                        # 'format' : '[height<=360][ext=mp4]',
                        'format' : 'best',
                        'youtube_include_dash_manifest' : False,
                        'nocheckcertificate' : True,
                        'debug_printtraffic' : True,
                        'ignoreerrors' : True,
                        'nooverwrites' : True,
                        'sleep_interval' : 1,
                        'max_sleep_interval' : 5,
                        'writesubtitles' : True,
                        'subtitlesformat' : "vtt",
                        'subtitleslangs' : SUB_LANG,
                        'postprocessors' : [{
                            'key' : 'FFmpegSubtitlesConvertor',
                            'format' : 'srt',
                        }],
                    }
        self._option.update(option)
        
    def download(self, target_id):
        success = False
        try:
            url = self._url % target_id
            destination = self._video_path / target_id
            
            self._path_check(destination)
            
            self._option['outtmpl'] = f'{destination}/{target_id}.%(ext)s'

            with YoutubeDL(self._option) as ydl:
                ydl.download([url])
                success = True

            subtitle_paths = sorted(glob( str(destination / '*.srt')))
            
            subtitle_downloaded = 1 if len(subtitle_paths) else 2
            
            return {
                'success' : success,
                'video_id' : target_id,
                'file_path' : f'{destination}/{target_id}.mp4',
                'subtitle_downloaded' : subtitle_downloaded,
                'subtitle_path' : {path.split('/')[-1].split('.')[-2] : path for path in subtitle_paths},
            }
            
        except Exception as e:
            logger.warning(e)
            return {
                'success' : success
            }

    def check_subtitle(self, target_id):
        url = self._url % target_id
        option = {
                    'logger' : MyLogger(),
                    'progress_hooks': [my_hook],
                    'debug_printtraffic' : True,
                    'ignoreerrors' : True,
                    'nooverwrites' : True,
                    'listsubtitles' : True,
                }
        with YoutubeDL(option) as ydl:
            res = ydl.download([url])
        
        return res


    def _path_check(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
    
if __name__ == "__main__":
    d = Downloader()
    print(d.download('l3UzNeUr8C8'))