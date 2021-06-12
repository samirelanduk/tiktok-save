#!/usr/bin/env python 

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
parser.add_argument("mode", type=str, nargs=1, choices=["liked", "bookmarked"], help="The file to convert.")
parser.add_argument("source", type=str, nargs=1, help="The tiktok JSON file.")
parser.add_argument("location", type=str, nargs=1, help="The folder to save to.")
args = parser.parse_args()
mode = args.mode[0]
source = args.source[0]
location = args.location[0]

# Open JSON
with open(source) as f: data = json.load(f)

# Get list
activity = data["Activity"]
videos = activity["Like List"]["ItemFavoriteList"] if mode == "liked" else \
 activity["Favorite Videos"]["FavoriteVideoList"]

# Initialise tiktok API connector
api = TikTokApi.get_instance()
did = str(random.randint(10000, 999999999))

# What videos are already accounted for?
existing_ids = get_existing_ids(location)
failed_ids = get_failed_ids(location)
videos = [v for v in videos if video_url_to_id(v["Link"]) not in existing_ids
        and video_url_to_id(v["Link"]) not in failed_ids]

# Worth doing anything?
if len(videos) == 0:
    print("Nothing new to download")
    sys.exit()

# Save videos and metadata
failures = []
for video in tqdm(videos):
    timestamp = date_to_timestamp(video["Date"])
    tiktok_id = video_url_to_id(video["Link"])
    tiktok_dict = api.get_tiktok_by_id(tiktok_id, custom_did=did)
    try:
        tiktok_data = api.get_Video_By_TikTok(tiktok_dict, custom_did=did)
    except:
        failures.append(tiktok_dict)
        record_failure(tiktok_id, location)
        continue
    save_files(location, tiktok_dict, tiktok_data, timestamp, tiktok_id)
    time.sleep(1) # don't be suspicious

# Any problems to report?
if len(failures): print("Failed downloads:", len(failures))
