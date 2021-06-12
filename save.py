#!/usr/bin/env python 

import argparse

parser = argparse.ArgumentParser(description="Save tiktok videos to disk.")
parser.add_argument("mode", type=str, nargs=1, choices=["liked", "bookmarked"], help="The file to convert.")
parser.add_argument("data", type=str, nargs=1, help="The tiktok JSON file.")
parser.add_argument("location", type=str, nargs=1, help="The folder to save to.")
args = parser.parse_args()
mode = args.mode[0]
data = args.data[0]
location = args.location[0]