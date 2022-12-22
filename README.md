# tiktok-save

A Python utility for backing up your liked and bookmarked videos on TikTok. It will download the videos themselves as mp4 files, and associated metadata for each video as JSON.

## Before Starting

You will need a JSON export of your TikTok data. TikTok lets you request this from the app, and it can take a few days for them to prepare this, so if you're planning on using this tool soon, consider requesting it now. If you have notifications turned off for TikTok, don't forget to check for it to be ready. You need the **JSON** version.

## Installation

```sh
git clone git@github.com:tosirisuk/tiktok-save.git tiktok-save
cd tiktok-save
pip3 install -r requirements.txt
```

If you get permission errors, try using `sudo` or using a virtual environment.

Then, install `playwright`

```sh
python3 -m playwright install
```

The main dependency here is [TikTok-Api](https://github.com/davidteather/TikTok-Api) - a great unofficial wrapper around the TikTok API. If you have any problems installing things, check the issues/docs there too.

playwright is a headless browser that TikTok-Api uses to access TikTok - you might need `sudo` privileges to install it, even in a virtual environment.

## Use

Create a folder for your liked videos and/or a folder for your bookmarked videos. Then run:

```sh
./save.py liked user_data.json liked_videos_path
```

and/or

```sh
./save.py bookmarked user_data.json bookmarked_videos_path
```

Here `user_data.json` is the TikTok JSON export, assuming it's in the current directory - provide the path to it if not.
You can request the `user_data.json` through the official TikTok application. It takes a couple of days for the TikTok to process your request.

Any failures (where a video no longer exists for example) are saved in a `failures.json` file, and won't be re-requested on later downloads. If you want to try previous failures, use the `--failures` argument.
