import os
import json
import time
from datetime import datetime
from tqdm import tqdm


def videos_to_check(videos, location, check_failures):
    """Get a subset of all videos to actually check."""

    existing_ids = get_existing_ids(location)
    failed_ids = get_failed_ids(location)
    
    def safe_video_url_to_id(video):
        url = video.get("link") or video.get("VideoLink")
        try:
            return video_url_to_id(url)
        except Exception:
            print(f"Warning: Could not extract ID from URL: {url}")
            return None

    if check_failures:
        # Only attempt to download previously failed videos
        return [v for v in videos if safe_video_url_to_id(v) in failed_ids]
    else:
        # Download new videos, skipping both existing and failed ones
        return [v for v in videos if safe_video_url_to_id(v) not in existing_ids
                and safe_video_url_to_id(v) not in failed_ids
                and safe_video_url_to_id(v) is not None]


def get_existing_ids(location):
    """Gets the video IDs already present in a directory."""
    files = os.listdir(location)
    video_ids = []
    for f in files:
        if f.endswith(".mp4"):
            # Try to extract the ID from the filename
            parts = f.split(".")
            if len(parts) > 1:
                video_id = parts[0]
                # If the ID contains underscores, take the last part
                if "_" in video_id:
                    video_id = video_id.split("_")[-1]
                video_ids.append(video_id)
    return video_ids


def get_failed_ids(location):
    """Gets the video IDs of previously failed videos."""
    try:
        with open(os.path.join(location, "logs", "download_failures.json"), "r") as f:
            return list(json.load(f).keys())
    except FileNotFoundError:
        return []


def date_to_timestamp(time):
    """Converts a string datetime to a UTC timestamp."""

    dt = datetime.strptime(f"{time}Z", "%Y-%m-%d %H:%M:%S%z")
    return int(datetime.timestamp(dt))


def video_url_to_id(url):
    """Converts a TikTok URL to the relevant ID."""

    return url.split("/")[-2]

def share_url_to_user(url):
    """Converts a TikTok share URL to a blank normal url."""

    userUrl = url.replace('share', '@')
    userUrl = userUrl.replace('tiktokv', 'tiktok')
    return userUrl

def save_files(location, tiktok_dict, tiktok_data, tiktok_id, mode):
    """Saves the two files to disk."""
    name = tiktok_id
    
    # Create main location directory if it doesn't exist
    os.makedirs(location, exist_ok=True)
    
    # Save video file in the main location
    if mode == "video":
        with open(os.path.join(location, f"{name}.mp4"), "wb") as f:
            f.write(tiktok_data)
    elif mode == "video_alt":
        with open(os.path.join(location, f"{name}.mp4"), "wb") as f:
            for chunk in tiktok_data.iter_content(chunk_size=1024):
                f.write(chunk)
    else:
        imageFolder = os.path.join(location, f"{name}")
        os.makedirs(imageFolder, exist_ok=True)
        for index, image in enumerate(tiktok_data):
            with open(os.path.join(imageFolder, f"{index}.jpeg"), "wb") as f:
                f.write(image)

    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(location, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Save JSON file in the logs directory
    with open(os.path.join(logs_dir, f"{name}.json"), "w") as f:
        json.dump(tiktok_dict, f, indent=4)

def record_failure(tiktok_id, error_message, location, author_unique_id):
    """Make a note that a certain video can't be downloaded."""

    file_location = os.path.join(location, "logs", "download_failures.json")
    if os.path.exists(file_location):
        with open(file_location) as f:
            failures = json.load(f)
    else:
        failures = {}
    failures[tiktok_id] = {
        "timestamp": time.time(),
        "error_message": error_message,
        "author_unique_id": author_unique_id
    }
    with open(file_location, "w") as f:
        json.dump(failures, f, indent=4)


def remove_failure(tiktok_id, location):
    """Remove a failure record."""

    file_location = os.path.join(location, "failures.json")
    with open(file_location) as f:
        failures = json.load(f)
        with open(file_location, "w") as f:
            json.dump({
                k: v for k, v in failures.items() if k != tiktok_id
            }, f, indent=4)