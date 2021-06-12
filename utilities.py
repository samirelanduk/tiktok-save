import os

def get_existing_ids(location):
    """Gets the video IDs already present in a directory."""

    files = os.listdir(location)
    return [f.split(".")[0] for f in files if f.endswith(".mp4")]


def video_url_to_id(url):
    """Converts a TikTok URL to the relevant ID."""

    return url.split("/")[-2]