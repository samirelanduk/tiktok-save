#!/usr/bin/env python 

import argparse
import ast
import asyncio
import json
import os
import random
import sys
import time
import traceback
from collections import defaultdict

import requests
from TikTokApi import TikTokApi
from tqdm import tqdm

from utilities import *


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
        parser.add_argument("mode", type=str, nargs=1, choices=["liked", "bookmarked", "watched"], help="The type of video to download.")
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
        activity = data["Your Activity"]
        if mode == "liked":
            videos = activity["LikeList"]["ItemFavoriteList"]
        elif mode == "bookmarked":
            videos = activity["Favorite Videos"]["FavoriteVideoList"]
        else:
            videos = activity["Watch History"]["VideoList"]

        # What videos are already accounted for?
        print("Checking for videos to download...")
        videos = videos_to_check(videos, location, check_failures)

        # Worth doing anything?
        if len(videos) == 0:
            print("Nothing new to download")
            sys.exit()

        # Save videos and metadata
        failures = load_failures(location)
        unique_ids_count = defaultdict(int)  # Use a defaultdict to store unique IDs and their failure counts
        for videoInfo in tqdm(videos):
            author_unique_id = "unknown"  # Default value
            try:
                # support for both likes and bookmarks
                link = share_url_to_user(videoInfo.get("link") or videoInfo.get("Link"))

                video = api.video(url=link)
                tiktok_id = video.id[:-1]

                # define variable as empty in case video info fails
                tiktok_dict = {}
                video_info = await video.info()
                tiktok_dict = video_info  # This is already a dictionary

                # Get author's uniqueID
                author_unique_id = video_info.get('author', {}).get('uniqueId', 'unknown')

                # Filter videos based on keywords
                if keywords:
                    try:
                        if not should_download(tiktok_dict, keywords):
                            tqdm.write(f"Skipping video {tiktok_id} as it doesn't match the keywords")
                            continue
                    except Exception as e:
                        tqdm.write(f"Error filtering video {tiktok_id}: {str(e)}")
                        continue

                # handle image posts here
                if "imagePost" in tiktok_dict:
                    imageBytes = download_images(tiktok_dict["imagePost"]["images"])
                    save_files(location, tiktok_dict, imageBytes, tiktok_id, "images")
                else:
                    video_bytes = await video.bytes()
                    save_files(location, tiktok_dict, video_bytes, tiktok_id, "video")

                # Remove from failures if it was successfully downloaded
                failures.pop(tiktok_id, None)

                time.sleep(1)  # don't be suspicious
            except Exception as e:
                error_message = f"Error processing video {link}: {str(e)}"

                # Retry video download using manual request method + alternative bitrate url
                if tiktok_dict is not None and "imagePost" not in tiktok_dict:
                    try:
                        altVideoBytes = alt_video_download(tiktok_dict)
                        save_files(location, tiktok_dict, altVideoBytes, tiktok_id, "video_alt")

                        failures.pop(tiktok_id, None)
                        time.sleep(1)  # don't be suspicious
                        continue
                    except Exception as e2:
                        error_message = f"Failed again for {link}: {str(e2)}"

                tqdm.write(error_message)
                failures[tiktok_id] = {
                    "link": link,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": time.time(),
                    "author_unique_id": author_unique_id
                }
                unique_ids_count[author_unique_id] += 1

        # Save updated failures
        save_failures(location, failures)
        print(f"Failed downloads: {len(failures)}")

        # Save unique IDs with failure counts to a file
        save_unique_ids_with_counts(location, unique_ids_count)

def download_images(images):
    """Based on this work https://github.com/financiallyruined/TikTok-Multi-Downloader"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'HX-Request': 'true',
        'HX-Trigger': 'search-btn',
        'HX-Target': 'tiktok-parse-result',
        'HX-Current-URL': 'https://tiktokio.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://tiktokio.com',
        'Connection': 'keep-alive',
        'Referer': 'https://tiktokio.com/'
    }

    imageData = []
    with requests.Session() as s:
        for imageDict in images:
            imgUrl = imageDict["imageURL"]["urlList"][0]
            imageData.append(s.get(imgUrl).content)

    return imageData

def alt_video_download(tiktok_dict):
    """Based on this work https://github.com/financiallyruined/TikTok-Multi-Downloader"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'HX-Request': 'true',
        'HX-Trigger': 'search-btn',
        'HX-Target': 'tiktok-parse-result',
        'HX-Current-URL': 'https://tiktokio.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://tiktokio.com',
        'Connection': 'keep-alive',
        'Referer': 'https://tiktokio.com/'
    }

    altVideoUrls = tiktok_dict["video"]["bitrateInfo"][0]["PlayAddr"]["UrlList"]
    for url in altVideoUrls:
        if url.startswith("https://www.tiktok.com"):
            with requests.Session() as s:
                videoStream = s.get(url, stream=True)

    return videoStream

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

def save_unique_ids_with_counts(location, unique_ids_count):
    """Save unique IDs with failure counts to a file."""
    file_path = os.path.join(location, "logs", "uniqueIDs.txt")
    with open(file_path, "w") as f:
        for unique_id, count in sorted(unique_ids_count.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{unique_id},{count}\n")
    print(f"Unique IDs of failed downloads with failure counts saved to {file_path}")

if __name__ == "__main__":
    asyncio.run(get_videos())
