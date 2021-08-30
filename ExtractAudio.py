import speech_recognition as sr
import moviepy.editor as mp
import math
import os

WINDOW_SIZE = 0.5
THRESHOLD = 0.335


class Extract:
    def __init__(
            self,
            video_id,
            video_type="mp4",
            audio_type="wav",
            temp_video_path='data/videos/',
            window_size=WINDOW_SIZE,
            threshold=THRESHOLD,
            subtitle_type='srt',
            language="en-GB"
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
        self.language = language
        self.temp_video_path = rf'{temp_video_path}/{video_id}/{video_id}.{video_type}'
        self.audio_path = self.temp_video_path.replace(video_type, audio_type)
        self.subtitle_path = self.temp_video_path.replace(
            video_type, subtitle_type)

    def __call__(self):
        pass

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
        # log = open('log/log.text', 'w')
        with self.sr.AudioFile(self.audio_path) as source:
            for (idx, _) in enumerate(self.subtitle):
                start, end = _
                self.recognizer.energy_threshold = 4000
                # self.recognizer.pause_threshold = 0.8
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(
                    source, offset=0, duration=(end-start))
                # print(audio.get_segment(start, end)
                with open(f'{idx}.wav', 'wb') as test:
                    test.write(audio.get_wav_data())
                if audio:
                    try:
                        string = self.recognizer.recognize_google(
                            audio, language=self.language, show_all=True)
                        print(start, end, string)
                    except sr.UnknownValueError as e:
                        print(e)
                    if type(string) is not list:
                        saveString = string['alternative'][0]['transcript']
                        saveformat = f'{idx}\n{start} --> {end}\n{saveString}\n\n'
                        self.subtitleSub.append(saveformat)
                        print(f"{start} - {end} {saveString}")
                else:
                    print('no audio')

        with open(self.subtitle_path, 'w') as f:
            f.writelines(self.subtitleSub)
        # log.close()

if __name__ == '__main__':
    # e = Extract('GE5E1nMLznY')
    # e = Extract('l3UzNeUr8C8')
    e = Extract('83cC2h35ZUM')
    myClip, file_length = e.cvtVideo2Audio()
    e.extract_sound(myClip, file_length)
    e.make_subtitle()
