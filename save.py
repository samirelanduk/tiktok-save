#!/usr/bin/env python 

import argparse
import json
import sys
import random
import time
from tqdm import tqdm
from TikTokApi import TikTokApi
from utilities import *
import asyncio
import traceback
import os
import ast

def parse_keywords(value):
    if value.startswith('[') and value.endswith(']'):
        try:
            return ast.literal_eval(value)
        except:
            pass
    return value.split()

async def get_videos():
    ms_token = os.environ.get("ms_token", None) # get your own ms_token from your cookies on tiktok.com
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
       
        # Parse script arguments
        parser = argparse.ArgumentParser(description="Save tiktok videos to disk.")
        parser.add_argument("mode", type=str, nargs=1, choices=["liked", "bookmarked"], help="The type of video to download.")
        parser.add_argument("source", type=str, nargs=1, help="The tiktok JSON file.")
        parser.add_argument("location", type=str, nargs=1, help="The folder to save to.")
        parser.add_argument("--failures", type=bool, nargs='?', const=True, default=False, help="Look at previous failures.")
        parser.add_argument("--keywords", nargs='+', help="List of keywords to filter videos")
        args = parser.parse_args()
        mode = args.mode[0]
        source = args.source[0]
        location = args.location[0]
        keywords = [k.lower() for k in args.keywords] if args.keywords else None
        
        # Create main location directory if it doesn't exist
        os.makedirs(location, exist_ok=True)

        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(location, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        check_failures = args.failures

        # Open JSON
        with open(source, encoding="utf8") as f: data = json.load(f)

        # Get list
        activity = data["Activity"]
        videos = activity["Like List"]["ItemFavoriteList"] if mode == "liked" else \
        activity["Favorite Videos"]["FavoriteVideoList"]
    
        # What videos are already accounted for?
        videos = videos_to_check(videos, location, check_failures)

        # Worth doing anything?
        if len(videos) == 0:
            print("Nothing new to download")
            sys.exit()

        # Save videos and metadata
        failures = load_failures(location)
        for videoInfo in tqdm(videos):
            try:
                timestamp = date_to_timestamp(videoInfo["Date"])
                video = api.video(url=videoInfo["Link"])
                tiktok_id = video.id[:-1]

                video_info = await video.info()
                tiktok_dict = video_info  # This is already a dictionary

                # Filter videos based on keywords
                if keywords:
                    try:
                        if not should_download(tiktok_dict, keywords):
                            print(f"Skipping video {tiktok_id} as it doesn't match the keywords")
                            continue
                    except Exception as e:
                        print(f"Error filtering video {tiktok_id}: {str(e)}")
                        continue

                video_bytes = await video.bytes()

                save_files(location, tiktok_dict, video_bytes, timestamp, tiktok_id)
                
                # Remove from failures if it was successfully downloaded
                failures.pop(tiktok_id, None)
                
                time.sleep(1)  # don't be suspicious
            except Exception as e:
                error_message = f"Error processing video {videoInfo['Link']}: {str(e)}"
                print(error_message)
                failures[tiktok_id] = {
                    "link": videoInfo["Link"],
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": time.time()
                }
        
        # Save updated failures
        save_failures(location, failures)
        print(f"Failed downloads: {len(failures)}")

def should_download(video_info, keywords):
    """Check if the video matches any of the given keywords."""
    def safe_lower(text):
        return text.lower() if isinstance(text, str) else str(text).lower()

    text_to_check = [
        safe_lower(video_info.get('desc', '')),
        *[safe_lower(tag.get('hashtagName', '')) for tag in video_info.get('textExtra', [])],
        *[safe_lower(word) for word in video_info.get('suggestedWords', [])]
    ]
    return any(keyword in ' '.join(text_to_check) for keyword in keywords)

def load_failures(location):
    try:
        with open(os.path.join(location, "logs", "download_failures.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_failures(location, failures):
    with open(os.path.join(location, "logs", "download_failures.json"), "w") as f:
        json.dump(failures, f, indent=4)

if __name__ == "__main__":
    asyncio.run(get_videos())
