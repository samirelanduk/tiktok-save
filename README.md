# tiktok-save

A Python utility for backing up your liked and bookmarked videos on TikTok. It will download the videos themselves as mp4 files, and associated metadata for each video as JSON.

## Before Starting

You will need a JSON export of your TikTok data. TikTok lets you request this from the app, and it can take a few days for them to prepare this, so if you're planning on using this tool soon, consider requesting it now. If you have notifications turned off for TikTok, don't forget to check for it to be ready. You need the **JSON** version.

## Installation

```bash
$ git clone https://github.com/samirelanduk/tiktok-save .
$ cd tiktok-save
$ python -m playwright install
$ pip install -r requirements.txt
```

If you get permission errors, try using `sudo` or using a virtual environment.

The main dependency here is [TikTok-Api](https://github.com/davidteather/TikTok-Api) - a great unofficial wrapper around the TikTok API. If you have any problems installing things, check the issues/docs there too.

playwright is a headless browser that TikTok-Api uses to access TikTok - you might need `sudo` privileges to install it, even in a virtual environment. If you still encounter issues, try `playwright install-deps`.

## Use

Create a folder for your liked videos and a folder for your bookmarked videos. Then, from the `tiktok-save` directory, run:

```bash
$ ./save.py liked user_data.json liked_videos_path
$ ./save.py bookmarked user_data.json bookmarked_videos_path
```

Here `user_data.json` is the TikTok JSON export, assuming it's in the current directory - provide the path to it if not.

Any failures (where a video no longer exists for example) are saved in a `download_failures.json` file, and won't be re-requested on later downloads. If you want to try previous failures, use the `--failures` argument.

### Parameters

- `<mode>`: Specify the type of videos to download. Options are:
  - `liked`: Download videos that you have liked.
  - `bookmarked`: Download videos that you have bookmarked.

- `<source>`: The path to the TikTok JSON file containing the video information.

- `<location>`: The directory where the downloaded videos and logs will be saved.

- `--failures`: (Optional) If specified, the tool will attempt to download only previously failed videos.

- `--keywords`: (Optional) A list of keywords seperated by spaces to filter the videos. Only videos containing these keywords in their description, hashtags, or suggested words will be downloaded. This is useful if you want to download videos related to a specific topic such as recipes.
    ex. `./save.py bookmarks user_data.json liked_videos --keywords recipe cooking food`

## Output

- Downloaded videos will be saved in the specified location.
- Metadata for each video will be saved as a JSON file in a `logs` directory within the specified location.
- Failed downloads will be recorded in `download_failures.json`.
- Unique IDs of failed downloads and their counts will be saved in `uniqueIDs.txt`.