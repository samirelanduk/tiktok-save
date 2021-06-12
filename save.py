#!/usr/bin/env python 

import argparse
import json

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
