#-*-coding:utf-8-*-

#!/usr/bin/python3

import os
from pathlib import Path
from shutil import copyfileobj

import requests
from lxml import html


BASE_URL = "https://www.xkcd.com/"
ARCHIVE = "https://www.xkcd.com/archive"
SAVE_DIRECTORY = Path('xkcd_comics')
LOGO = """
       _           _                      
 tiny | |  image  | | downloader for
 __  _| | _____ __| |  ___ ___  _ __ ___  
 \ \/ / |/ / __/ _` | / __/ _ \| '_ ` _ \ 
  >  <|   < (_| (_| || (_| (_) | | | | | |
 /_/\_\_|\_\___\__,_(_)___\___/|_| |_| |_|
 version: 0.4
"""


def show_logo():
    print(LOGO)


def fetch_url(url: str) -> requests.Response:
    return requests.get(url)


def head_option(values: list) -> str:
    return next(iter(values), None)


def get_latest_comic_number(url: str) -> int:
    page = fetch_url(url)
    tree = html.fromstring(page.content)
    newest_comic = head_option(
        tree.xpath('//*[@id="middleContainer"]/a[1]/@href'))
    return int(newest_comic.replace("/", ""))


def get_images_from_page(url: str) -> str:
    page = fetch_url(url)
    tree = html.fromstring(page.content)
    return head_option(tree.xpath('//*[@id="comic"]//img/@src'))


def clip_url(img: str) -> str:
    return img.rpartition("/")[-1]


def make_dir():
    return os.makedirs(SAVE_DIRECTORY, exist_ok=True)


def save_image(img: str):
    comic_name = clip_url(img)
    print(f"Downloading: {comic_name}")
    f_name = SAVE_DIRECTORY / comic_name
    with requests.get("https:" + img, stream=True) as img, open(f_name, "wb") \
            as output:
        copyfileobj(img.raw, output)


def get_xkcd():
    make_dir()
    latest_comic = get_latest_comic_number(ARCHIVE)
    for page in reversed(range(1, latest_comic + 1)):
        print(f"Fetching page {page} out of {latest_comic}")
        try:
            save_image(get_images_from_page(f"{BASE_URL}{page}/"))
        except (ValueError, requests.exceptions.MissingSchema):
            print(f"WARNING: Invalid comic image source url.")
            continue


def main():
    show_logo()
    get_xkcd()


if __name__ == '__main__':
    main()
