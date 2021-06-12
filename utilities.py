import os
from datetime import datetime

def get_existing_ids(location):
    """Gets the video IDs already present in a directory."""

    files = os.listdir(location)
    return [f.split("_")[0] for f in files if f.endswith(".mp4")]


def date_to_timestamp(time):
    """Converts a string datetime to a UTC timestamp."""

    dt = datetime.strptime(f"{time}Z", "%Y-%m-%d %H:%M:%S%z")
    return int(datetime.timestamp(dt))


def video_url_to_id(url):
    """Converts a TikTok URL to the relevant ID."""

    return url.split("/")[-2]