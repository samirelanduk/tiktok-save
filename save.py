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





# Initialise tiktok API connector
async def get_videos():

    ms_token = os.environ.get("ms_token", None) # get your own ms_token from your cookies on tiktok.com
    #ydl_opts = {}
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
       

        #ms_token = os.environ.get("ms_token", None) # get your own ms_token from your cookies on tiktok.com
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
    
        did = str(random.randint(10000, 999999999))
        #user = api.user("therock")
        #user_data = await user.info()
        #with open(os.path.join("saved_tiktoks","user_data.json"), "wb") as f:
         #   f.write(user_data)
        # What videos are already accounted for?
        videos = videos_to_check(videos, location, check_failures)

        # Worth doing anything?
        if len(videos) == 0:
            print("Nothing new to download")
            sys.exit()

        # Save videos and metadata
        failures = []
        for videoInfo in tqdm(videos):
            try:
                timestamp = date_to_timestamp(videoInfo["Date"])
                video = api.video(url=videoInfo["Link"])
                tiktok_id = video.id[:-1]

                video_info = await video.info()
                tiktok_dict = json.dumps(video_info, indent=4)
                video_bytes = await video.bytes()

                save_files(location, tiktok_dict, video_bytes, timestamp, tiktok_id)
                if check_failures:
                    remove_failure(tiktok_id, location)
                
                time.sleep(1)  # don't be suspicious
            except Exception as e:
                error_message = f"Error processing video {videoInfo['Link']}: {str(e)}"
                print(error_message)
                failures.append({
                    "id": tiktok_id,
                    "link": videoInfo["Link"],
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                record_failure(tiktok_id, error_message, location)
            
        # Log all failures at the end
        if failures:
            print(f"Failed downloads: {len(failures)}")
            with open(os.path.join(location, "download_failures.json"), "w") as f:
                json.dump(failures, f, indent=4)

if __name__ == "__main__":
    asyncio.run(get_videos())
