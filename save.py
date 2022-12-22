#!/usr/bin/env python3

import argparse
import json
import sys
import random
import time
from tqdm import tqdm
from TikTokApi import TikTokApi
from utilities import *

# Parse script arguments
parser = argparse.ArgumentParser(description="Save tiktok videos to disk.")
parser.add_argument("mode", type=str, nargs=1, choices=["liked", "bookmarked"], help="The type of video to download.")
parser.add_argument("source", type=str, nargs=1, help="The tiktok JSON file.")
parser.add_argument("location", type=str, nargs=1, help="The folder to save to.")
parser.add_argument("--failures", type=bool, nargs='?', const=True, default=False, help="Look at previous failures.")
args = parser.parse_args()
mode = args.mode[0]
source = args.source[0]
location = args.location[0]
check_failures = args.failures

# Open JSON
with open(source, encoding="utf8") as f: data = json.load(f)

# Get list
activity = data["Activity"]
videos = activity["Like List"]["ItemFavoriteList"] if mode == "liked" else \
 activity["Favorite Videos"]["FavoriteVideoList"]

# Initialise tiktok API connector
api = TikTokApi.get_instance()
did = str(random.randint(10000, 999999999))

# What videos are already accounted for?
videos = videos_to_check(videos, location, check_failures)

# Worth doing anything?
if len(videos) == 0:
    print("Nothing new to download")
    sys.exit()

# Save videos and metadata
failures = []
for video in tqdm(videos):
    timestamp = date_to_timestamp(video["Date"])
    tiktok_id = video_url_to_id(video.get("Link", video.get("VideoLink")))
    tiktok_dict = api.get_tiktok_by_id(tiktok_id, custom_did=did)
    uniqueId = "unknown"
    try:
        uniqueId = tiktok_dict["itemInfo"]["itemStruct"]["author"]["uniqueId"]
        tiktok_data = api.get_video_by_tiktok(tiktok_dict, custom_did=did)
        if check_failures: remove_failure(tiktok_id, location)
    except Exception as e:
        failures.append(tiktok_dict)
        record_failure(tiktok_id, location)
        continue
    save_files(location, tiktok_dict, tiktok_data, timestamp, tiktok_id,uniqueId)
    time.sleep(1) # don't be suspicious

# Any problems to report?
if len(failures): print("Failed downloads:", len(failures))
