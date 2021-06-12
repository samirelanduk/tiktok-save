#!/usr/bin/env python 

import argparse
import json
import random
import os
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
videos = [v for v in videos if video_url_to_id(v["Link"]) not in existing_ids]

# Save videos and metadata
failures = []
for video in tqdm(videos):
    tiktok_id = video_url_to_id(video["Link"])
    tiktok_dict = api.get_tiktok_by_id(tiktok_id, custom_did=did)
    try:
        tiktok_data = api.get_Video_By_TikTok(tiktok_dict, custom_did=did)
    except:
        failures.append(tiktok_dict)
        continue
    with open(os.path.join(location, f"{tiktok_id}.mp4"), "wb") as f:
        f.write(tiktok_data)
    with open(os.path.join(location, f"{tiktok_id}.json"), "w") as f:
        json.dump(tiktok_dict, f, indent=4)
    time.sleep(1) # don't be suspicious
if len(failures): print("Failed downloads:", len(failures))
