import requests
import uuid

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

def save_video(video_url: str) -> str:
    """
    Saves a video from a given URL and returns the path to the video.

    Args:
        video_url (str): The URL of the video to save.
        directory (str): The path of the temporary directory to save the video to

    Returns:
        str: The path to the saved video.
    """
    video_id = uuid.uuid4()
    video_path = f"../temp/{video_id}.mp4"
    with open(video_path, "wb") as f:
        f.write(requests.get(video_url).content)

    return video_path

def search_for_stock_videos(query: str, min_dur: int) -> List[str]:
    """
    Searches for stock videos based on a query.

    Args:
        query (str): query to use when searching

    Returns:
        List[str]: A list of stock videos.
    """
    
    # Build headers
    headers = {
        "Authorization": os.getenv('PEXELS_KEY')
    }

    NUM_VIDEOS = 5

    # Build URL
    query = query
    qurl = f"https://api.pexels.com/videos/search?query={query}&per_page={NUM_VIDEOS}"

    # Send the request
    r = requests.get(qurl, headers=headers)

    # Parse the response
    response = r.json()

    # Parse each video
    raw_urls = []
    video_urls = []
    video_res = 0
    try:
        # loop through each video in the result
        for i in range(NUM_VIDEOS):
            #check if video has desired minimum duration
            if response["videos"][i]["duration"] < min_dur:
                continue
            raw_urls = response["videos"][i]["video_files"]
            temp_video_url = ""
            
            # loop through each url to determine the best quality
            for video in raw_urls:
                # Check if video has a valid download link
                if ".com/video-files" in video["link"]:
                    # Only save the URL with the largest resolution
                    if (video["width"] * video["height"]) > video_res:
                        temp_video_url = video["link"]
                        video_res = video["width"]*video["height"]
                        
            # add the url to the return list if it's not empty
            if temp_video_url != "":
                video_urls.append(temp_video_url)
                
    except Exception as e:
        print("[-] No Videos found.")
        print(e)

    # Let user know
    print(f"\t=> \"{query}\" found {len(video_urls)} Videos")

    # save video and return local path to video 
    video_paths = []
    for video in video_urls:
        video_paths.append(save_video(video))

    return video_paths