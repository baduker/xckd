#!/usr/bin/python3

import os
import sys
import time
import concurrent.futures
from pathlib import Path
from shutil import copyfileobj


import requests
from lxml import html


BASE_URL = "https://www.xkcd.com/"
SAVE_DIRECTORY = Path('xkcd_comics')


def show_logo():
    logo = """
       _           _                      
 tiny | |  image  | | downloader for
 __  _| | _____ __| |  ___ ___  _ __ ___  
 \ \/ / |/ / __/ _` | / __/ _ \| '_ ` _ \
  >  <|   < (_| (_| || (_| (_) | | | | | |
 /_/\_\_|\_\___\__,_(_)___\___/|_| |_| |_|
 version: 0.8.1
 """
    return print(logo)


def fetch_url(url: str) -> requests.Response:
    return requests.get(url)


def head_option(values: list) -> str:
    return next(iter(values), None)


def get_penultimate(url: str) -> int:
    page = fetch_url(url)
    tree = html.fromstring(page.content)
    newest_comic = head_option(
        tree.xpath('//*[@id="middleContainer"]/a[1]/@href'))
    return int(newest_comic.replace("/", ""))


def get_images_from_page(url: str) -> str:
    page = fetch_url(url)
    tree = html.fromstring(page.content)
    return head_option(tree.xpath('//*[@id="comic"]//img/@src'))


def get_number_of_pages(latest_comic: int) -> int:
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


def clip_url(img: str) -> str:
    return img.rpartition("/")[-1]


def make_dir():
    return os.makedirs(SAVE_DIRECTORY, exist_ok=True)


def save_image(comic_id: str, img: str):
    comic_name = comic_id + "_" + clip_url(img)
    print(f"Downloading: {comic_name}")
    f_name = SAVE_DIRECTORY / comic_name
    with requests.get("https:" + img, stream=True) as img, open(f_name, "wb") \
            as output:
        copyfileobj(img.raw, output)


def show_time(seconds: int) -> int:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    time_elapsed = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return time_elapsed


def get_xkcd():
    show_logo()
    make_dir()

    collect_garbage = []
    latest_comic = get_penultimate(f"{BASE_URL}archive")
    pages = get_number_of_pages(latest_comic)

    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for page in reversed(range(latest_comic-pages + 1, latest_comic + 1)):
            print(f"Fetching page {page} out of {latest_comic}")
            try:
                url = get_images_from_page(f"{BASE_URL}{page}/")
                executor.submit(save_image, str(page), url)
            except (ValueError, AttributeError,
                    requests.exceptions.MissingSchema):
                print(f"WARNING: Invalid comic image source url.")
                collect_garbage.append(f"{BASE_URL}{page}")
                continue
    end = time.time()

    print(f"Downloaded {pages} comic(s) in {show_time(int(end - start))}.")

    if len(collect_garbage) > 0:
        print("However, was unable to download images for these pages:")
        print("\n".join(page for page in collect_garbage))


def main():
    get_xkcd()


if __name__ == '__main__':
    main()
