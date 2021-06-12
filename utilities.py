import os
import json
import time
from datetime import datetime

def get_existing_ids(location):
    """Gets the video IDs already present in a directory."""

    files = os.listdir(location)
    return [f.split(".")[0].split("_")[1] for f in files if f.endswith(".mp4")]


def get_failed_ids(location):
    """Gets the video IDs of previously failed videos."""

    try:
        with open(os.path.join(location, "failures.json")) as f:
            return list(json.load(f).keys())
    except FileNotFoundError: return []


def date_to_timestamp(time):
    """Converts a string datetime to a UTC timestamp."""

    dt = datetime.strptime(f"{time}Z", "%Y-%m-%d %H:%M:%S%z")
    return int(datetime.timestamp(dt))


def video_url_to_id(url):
    """Converts a TikTok URL to the relevant ID."""

    return url.split("/")[-2]


def save_files(location, tiktok_dict, tiktok_data, timestamp, tiktok_id):
    """Saves the two files to disk."""

    with open(os.path.join(location, f"{timestamp}_{tiktok_id}.mp4"), "wb") as f:
        f.write(tiktok_data)
    with open(os.path.join(location, f"{timestamp}_{tiktok_id}.json"), "w") as f:
        json.dump(tiktok_dict, f, indent=4)


def record_failure(tiktok_id, location):
    """Make a note that a certain video can't be downloaded."""

    file_location = os.path.join(location, "failures.json")
    if os.path.exists(file_location):
        with open(file_location) as f:
            failures = json.load(f)
    else:
        failures = {}
    failures[tiktok_id] = time.time()
    with open(file_location, "w") as f:
        json.dump(failures, f, indent=4)