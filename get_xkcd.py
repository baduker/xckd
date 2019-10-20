#!/usr/bin/python3

import os
import sys
import time
import json
import concurrent.futures
from pathlib import Path
from shutil import copyfileobj

import requests


SAVE_DIRECTORY = Path('xkcd_comics')
LOGO = """
       _           _                      
 tiny | |  image  | | downloader for
 __  _| | _____ __| |  ___ ___  _ __ ___  
 \ \/ / |/ / __/ _` | / __/ _ \| '_ ` _ \ 
  >  <|   < (_| (_| || (_| (_) | | | | | |
 /_/\_\_|\_\___\__,_(_)___\___/|_| |_| |_|
 version: 0.9.3
 """


def show_logo():
    return LOGO


def get_current_comic() -> int:
    current_comic = requests.get("https://xkcd.com/info.0.json").json()
    return int(current_comic["num"])


def get_images_from_page(comic_number: str) -> str:
    request = requests.get(f"https://xkcd.com/{comic_number}/info.0.json")
    if request.status_code <= 299:
        return request.json()["img"]


def get_comic_name_and_date(comic_number: str) -> str:
    request = requests.get(
        f"https://xkcd.com/{comic_number}/info.0.json").json()
    comic_name = request["safe_title"].replace(" ", "_")
    comic_date = "-".join([request["year"], request["month"], request["day"]])
    return comic_name + "_" + comic_date


def get_number_of_comics_to_download(latest_comic: int) -> int:
    print(f"There are {latest_comic} comics.")
    print(f"How many do you want to download? Type 0 to exit.")
    while True:
        try:
            number_of_comics = int(input(">> "))
        except ValueError:
            print("Error: Expected a number. Try again.")
            continue
        if number_of_comics > latest_comic or number_of_comics < 0:
            print("Error: Incorrect number of comics. Try again.")
            continue
        elif number_of_comics == 0:
            sys.exit()
        return number_of_comics


def make_dir():
    return os.makedirs(SAVE_DIRECTORY, exist_ok=True)


def save_image(comic_id: str, img: str):
    comic_name = get_comic_name_and_date(comic_id) + ".png"
    print(f"Downloading: {comic_name}")
    f_name = SAVE_DIRECTORY / comic_name
    with requests.get(img, stream=True) as img, open(f_name, "wb") \
            as output:
        copyfileobj(img.raw, output)


def show_time(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    time_elapsed = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return time_elapsed


def get_xkcd():
    show_logo()
    make_dir()

    collect_garbage = []
    latest_comic = get_current_comic()
    pages = get_number_of_comics_to_download(latest_comic)
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for page in reversed(range(
                latest_comic - (pages + 1), latest_comic + 1)):
            print(f"Fetching page {page} out of {latest_comic}")
            try:
                url = get_images_from_page(str(page))
                executor.submit(save_image, str(page), url)
            except (ValueError, AttributeError,
                    requests.exceptions.MissingSchema):
                print(f"WARNING: Invalid comic image source url.")
                collect_garbage.append(f"{page}")
                continue
    end = time.time()
    print(f"Downloaded {pages} comic(s) in {show_time(int(end - start))}.")
    if len(collect_garbage) > 0:
        print(f"However, was unbale to fetch these comic urls:")
        for invalid_url in collect_garbage:
            print(f"{invalid_url}")


def main():
    get_xkcd()


if __name__ == '__main__':
    main()
