from django.shortcuts import render
from django.http import HttpResponse

import os
from .utils import gpt
from .utils import videosearch
from .utils import voice
from .utils import video

# Create your views here.
def index(request):
    # if not os.path.exists("../temp"):
    #     os.mkdir("../temp")

    # TOPIC = "black people"
    # script = gpt.generate_script(TOPIC, 3)
    # video_paths = videosearch.search_for_stock_videos(TOPIC, 1)
    # if voice.tts(script) != "error":
    #     subtitle_path = video.generate_subtitles("../temp/tts.mp3")
    #     combined_video_path = video.combine_videos(video_paths, 30, 10,4)
    #     video.generate_video(combined_video_path, "../temp/tts.mp3", subtitle_path, 2, "100,100", "black")
    # else:
    #     print("[-] Aborting video creation process as tts service failed. Please try again in a few minutes")
    fartsmart = video.generate_video("../temp/615576f7-18a7-4f29-92c1-3dd51767493e.mp4", "../temp/tts.mp3", "../temp/788f636f-eade-4ef7-aa36-45a8573a188b.srt", 2, "540,960", "white")


    return render(request, "home/index.html", {"response": "hi"})

def generate(request):
    if not os.path.exists("../temp"):
        os.mkdir("../temp")

    TOPIC = "asian history in the 1900s"
    script = gpt.generate_script(TOPIC, 3)
    video_paths = videosearch.search_for_stock_videos(TOPIC, 1)
    if voice.tts(script) != "error":
        subtitle_path = video.generate_subtitles("../temp/tts.mp3")
        combined_video_path = video.combine_videos(video_paths, 30, 10, 2)
        video.generate_video(combined_video_path, "../temp/tts.mp3", subtitle_path, 2, "980,200", "white")
    else:
        print("[-] Aborting video creation process as tts service failed. Please try again in a few minutes")

    return render(request, "home/index.html", {"response": script})
    