from django.shortcuts import render, redirect
from django.http import HttpResponse

import os
import requests
from .utils import gpt, videosearch, voice, video

# Create your views here.
def index(request):
    return render(request, "generate/index.html", {})

def loading(request):
    return render(request, "generate/loading.html", {"topic": request.GET.get("topic")})
    
def generate(request):
    topic = request.GET.get("topic")
    __api_calls(topic)
    return redirect("generate:index")

def __api_calls(topic):
    print(f"[+] Generating video for {topic}")
    if not os.path.exists("../temp"):
        os.mkdir("../temp")

    script = gpt.generate_script(topic, 2)
    video_paths = videosearch.search_for_stock_videos(topic, 2)
    if voice.tts(script) != "error":
        subtitle_path = video.generate_subtitles("../temp/tts.mp3")
        length = video.subtitles_length(subtitle_path)
        combined_video_path = video.combine_videos(video_paths, length, 10, 2)
        video.generate_video(combined_video_path, "../temp/tts.mp3", subtitle_path, 2, "white")
    else:
        print("[-] Aborting video creation process as tts service failed, please try again.")