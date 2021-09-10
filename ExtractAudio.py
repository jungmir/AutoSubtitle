import speech_recognition as sr
import moviepy.editor as mp
import math
import requests
import os

WINDOW_SIZE = 0.5
THRESHOLD = 0.3
SUBTITLE_TYPE = 'srt'


class Extract:
    def __init__(
            self,
            video_id,
            video_type="mp4",
            audio_type="wav",
            temp_video_path='data/videos/',
            window_size=WINDOW_SIZE,
            threshold=THRESHOLD,
            language="en-GB",
            callback=None
    ):
        self.WINDOW_SIZE = window_size
        self.THRESHOLD = threshold
        self.sr = sr
        self.recognizer = sr.Recognizer()
        self.subtitle = []
        self.subtitleSub = []
        self.video_name = video_id
        self.video_type = video_type
        self.audio_type = audio_type
        self.subtitle_type = SUBTITLE_TYPE
        self.callback = callback
        self.language = language
        self.temp_video_path = rf'{temp_video_path}/{video_id}/{video_id}.{video_type}'
        self.audio_path = self.temp_video_path.replace(video_type, audio_type)
        self.subtitle_path = self.temp_video_path.replace(
            video_type, SUBTITLE_TYPE)

    def __call__(self):
        pass

    def extract(self):
        try:
            if self.callback:
                requests.post(self.callback, data={'task': 'make_subtitle', 'status' : 'start', 'progress': 0})
                
            myClip, file_length = self.cvtVideo2Audio()
            self.extract_sound(myClip, file_length)
            self.make_subtitle()

            if self.callback:
                requests.post(self.callback, data={'task': 'make_subtitle', 'status' : 'complete', 'progress': 100})

        except Exception as e:
            requests.post(self.callback, data={'task': 'make_subtitle', 'status' : 'error', 'progress': 0, 'msg': e})

        return self.subtitle_path

    def cvtVideo2Audio(self):
        video = mp.VideoFileClip(self.temp_video_path)
        video.audio.write_audiofile(self.audio_path)
        myClip = mp.VideoFileClip(self.temp_video_path)
        fileLegth = math.floor(myClip.audio.end / self.WINDOW_SIZE)
        return (myClip, fileLegth)

    def extract_sound(self, myClip, file_length):
        isStartSpeak = True
        for i in range(file_length):
            s = myClip.audio.subclip(
                i * self.WINDOW_SIZE, (i + 1) * self.WINDOW_SIZE)
            if s.max_volume() > self.THRESHOLD:
                if isStartSpeak:
                    startTime = i * self.WINDOW_SIZE

                isStartSpeak = False
            else:
                if not isStartSpeak:
                    endTime = i * self.WINDOW_SIZE
                    self.subtitle.append((startTime, endTime))
                    print(f'{startTime} - {endTime}')

                isStartSpeak = True

    def make_subtitle(self):
        subtitle_index = 1
        with self.sr.AudioFile(self.audio_path) as source:
            for (idx, _) in enumerate(self.subtitle):
                start, end = _
                # self.recognizer.energy_threshold = 4000
                # self.recognizer.pause_threshold = 0.8
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(
                    source, offset=0, duration=(end-start))
                
                # 테스트 코드 (오디오 영역이 잘 분리 되는지 확인을 위한)
                # with open(f'{idx}.wav', 'wb') as test:
                #     test.write(audio.get_wav_data())
                if audio:
                    try:
                        string = self.recognizer.recognize_google(
                            audio, language=self.language, show_all=True)
                        print(start, end, string)
                    except sr.UnknownValueError as e:
                        print(e)
                    if type(string) is not list:
                        saveString = string['alternative'][0]['transcript']
                        start_time = self.get_timestamp(start)
                        end_time = self.get_timestamp(end)
                        saveformat = f'{subtitle_index}\n{start_time} --> {end_time}\n{saveString}\n\n'
                        self.subtitleSub.append(saveformat)
                        subtitle_index += 1
                        print(f"{start} - {end} {saveString}")
                    if self.callback:
                        progress = int(idx / len(self.subtitle))
                        requests.post(self.callback, data={'task': 'make_subtitle', 'status': 'running', 'progress': progress})
                else:
                    print('no audio')

        with open(self.subtitle_path, 'w') as f:
            f.writelines(self.subtitleSub)

    def get_timestamp(self, time):
        result = int(time * 1000) # cvt sec to ms
        hour = minute = second = millisecond = 0
        millisecond = result % 1000
        result //= 1000
        second = result % 60
        result //= 60
        minute = result %  60
        result //= 60
        hour = result
        print(time, hour, minute, second, millisecond)
        return "{hour:02d}:{minute:02d}:{second:02d},{millisecond:03d}".format(hour=hour, minute=minute, second=second, millisecond=millisecond)

if __name__ == '__main__':
    # e = Extract('GE5E1nMLznY')
    # e = Extract('l3UzNeUr8C8')
    e = Extract('83cC2h35ZUM')
    e.extract()
