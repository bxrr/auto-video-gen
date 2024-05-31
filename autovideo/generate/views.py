from django.shortcuts import render, redirect

import os
from .utils import gpt, videosearch, voice, video

# Create your views here.
def index(request):
    return render(request, "generate/index.html", {})

def generate(request):
    topic = request.GET.get("topic")
    __api_calls(topic)
    return redirect("/")

def __api_calls(topic):
    print("[+] Generating video...")
    if not os.path.exists("../temp"):
        os.mkdir("../temp")

    script = gpt.generate_script(topic, 3)
    video_paths = videosearch.search_for_stock_videos(topic, 2)
    if voice.tts(script) != "error":
        subtitle_path = video.generate_subtitles("../temp/tts.mp3")
        combined_video_path = video.combine_videos(video_paths, 60, 10, 2)
        video.generate_video(combined_video_path, "../temp/tts.mp3", subtitle_path, 2, "white")
    else:
        print("[-] Aborting video creation process as tts service failed. Please try again in a few minutes")