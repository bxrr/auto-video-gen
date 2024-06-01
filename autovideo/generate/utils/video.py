import os
import uuid

import requests
import srt_equalizer
import assemblyai as aai

from typing import List
from moviepy.editor import *
from dotenv import load_dotenv
from datetime import timedelta
from moviepy.video.fx.all import crop
from moviepy.video.tools.subtitles import SubtitlesClip

load_dotenv()

ASSEMBLY_AI_KEY= os.getenv("ASSEMBLY_AI_KEY")

def generate_subtitles(audio_path: str) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.

    Returns:
        str: The generated subtitles
    """

    subtitles_path = f"../temp/{uuid.uuid4()}.srt"

    aai.settings.api_key = ASSEMBLY_AI_KEY
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_path)
    subtitles = transcript.export_subtitles_srt()
    with open(subtitles_path, "w") as file:
        file.write(subtitles)

    # Equalize subtitles
    srt_equalizer.equalize_srt_file(subtitles_path, subtitles_path, 10)

    print("[+] Subtitles generated.")
    return subtitles_path

def subtitles_length(subtitles_path: str) -> int:
    """
    Looks at the subtitles file to see how long the video should be

    Args:
        subtitles_path (str): path to subtitles file
    
    Returns:
        int: Number of seconds the video should be
    """

    with open(subtitles_path, "r") as file:
        line = file.read().replace("\n","").split(" --> ")[-1]
        timestamp = int(line.split(",")[0].split(":")[-1])
        return timestamp + 1

def combine_videos(video_paths: List[str], max_duration: int, max_clip_duration: int, threads: int) -> str:
    """
    Combines a list of videos into one video and returns the path to the combined video.

    Args:
        video_paths (List): A list of paths to the videos to combine.
        max_duration (int): The maximum duration of the combined video.
        max_clip_duration (int): The maximum duration of each clip.
        threads (int): The number of threads to use for the video processing.

    Returns:
        str: The path to the combined video.
    """
    video_id = uuid.uuid4()
    combined_video_path = f"../temp/{video_id}.mp4"
    
    # Required duration of each clip
    req_dur = max_duration / len(video_paths)

    print("[+] Combining videos...")
    print(f"[+] Each clip will be maximum {req_dur} seconds long.")

    clips = []
    tot_dur = 0
    # Add downloaded clips over and over until the duration of the audio (max_duration) has been reached
    while tot_dur < max_duration:
        for video_path in video_paths:
            clip = VideoFileClip(video_path)
            clip = clip.without_audio()
            # Check if clip is longer than the remaining audio
            if (max_duration - tot_dur) < clip.duration:
                clip = clip.subclip(0, (max_duration - tot_dur))
            # Only shorten clips if the calculated clip length (req_dur) is shorter than the actual clip to prevent still image
            elif req_dur < clip.duration:
                clip = clip.subclip(0, req_dur)
            clip = clip.set_fps(30)

            # Not all videos are same size,
            # so we need to resize them
            if round((clip.w/clip.h), 4) < 0.5625:
                clip = crop(clip, width=clip.w, height=round(clip.w/0.5625), \
                            x_center=clip.w / 2, \
                            y_center=clip.h / 2)
            else:
                clip = crop(clip, width=round(0.5625*clip.h), height=clip.h, \
                            x_center=clip.w / 2, \
                            y_center=clip.h / 2)
            clip = clip.resize((1080, 1920))

            if clip.duration > max_clip_duration:
                clip = clip.subclip(0, max_clip_duration)

            clips.append(clip)
            tot_dur += clip.duration

    final_clip = concatenate_videoclips(clips)
    final_clip = final_clip.set_fps(30)
    final_clip.write_videofile(combined_video_path, threads=threads)

    return combined_video_path

def generate_video(combined_video_path: str, tts_path: str, subtitles_path: str, threads: int, text_color: str) -> str:
    """
    This function creates the final video, with subtitles and audio.

    Args:
        combined_video_path (str): The path to the combined video.
        tts_path (str): The path to the text-to-speech audio.
        subtitles_path (str): The path to the subtitles.
        threads (int): The number of threads to use for the video processing.
        subtitles_position (str): The position of the subtitles.

    Returns:
        str: The path to the final video.
    """
    generator = lambda txt: TextClip(
        txt,
        font="./fonts/bold_font.ttf",
        fontsize=100,
        color=text_color,
        stroke_color="black",
        stroke_width=5,
    )

    # Burn the subtitles into the video
    subtitles = SubtitlesClip(subtitles_path, generator)
    result = CompositeVideoClip([
        VideoFileClip(combined_video_path),
        subtitles.set_pos(('center', 'center'))
    ])
    

    # Add the audio
    audio = AudioFileClip(tts_path)
    result = result.set_audio(audio)

    result.write_videofile("../temp/output.mp4", threads=threads or 2)

    return "output.mp4"
