import speech_recognition as sr
import moviepy.editor as mp
import math

def cvtVideo2Audio(source, target):
    video = mp.VideoFileClip(source)
    video.audio.write_audiofile(target)

# tmpVideoPath = r'data/videos/8FD70u3bRRk/8FD70u3bRRk.mp4'
# audioPath = r'data/videos/8FD70u3bRRk/8FD70u3bRRk.wav'
videoId = '8FD70u3bRRk'
tmpVideoPath = r'data/videos/' + videoId + '/' + videoId + '.mp4'
audioPath = r'data/videos/' + videoId + '/' + videoId + '.wav'
subtitlePath = r'data/videos/' + videoId + '/' + videoId + '.srt'

windowSize = 1
THRESHOLD = 0.3

cvtVideo2Audio(tmpVideoPath, audioPath)

myClip = mp.VideoFileClip(tmpVideoPath)

fileLegth = math.floor(myClip.audio.end / windowSize)

r = sr.Recognizer()

subtitle = []
subtitleSub = []

isStartSpeak = True
startTime = 0
endTime = 0

print(fileLegth)
for i in range(fileLegth):
    s = myClip.audio.subclip(i * windowSize, (i + 1) * windowSize)
    if s.max_volume() > THRESHOLD:
        if isStartSpeak:
            startTime = i * windowSize
            
        isStartSpeak = False
    else:
        if not isStartSpeak:
            endTime = i * windowSize
            subtitle.append((startTime, endTime))
            print(f'{startTime} - {endTime}')
            
        isStartSpeak = True
        
with sr.AudioFile(audioPath) as source:
    for (idx, _) in enumerate(subtitle):
        start, end = _
        audio = r.record(source, offset=0, duration=(end-start))
        if audio:
            string = r.recognize_google(audio, language='ko-KR', show_all=True)
            if type(string) is not list:
                saveString = string['alternative'][0]['transcript']
                saveformat = f'{idx}\n{start} --> {end}\n{saveString}\n\n'
                subtitleSub.append(saveformat)
                print(f"{start} - {end} {saveString}")
        else:
            print('no audio')
            
with open(subtitlePath, 'w') as f:
    f.writelines(subtitleSub)