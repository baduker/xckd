#!/usr/bin/python3

import os
import requests


from bs4 import BeautifulSoup as bs
from pathlib import Path
from shutil import copyfileobj


BASE_URL = "https://www.xkcd.com/"
CURRENT_MAX_PAGE = 2184
SAVE_DIRECTORY = Path('xkcd_comics')
LOGO = """
 image_downloader _for
__  _| | _____ __| |
\ \/ / |/ / __/ _` |
 >  <|   < (_| (_| |
/_/\_\_|\_\___\__,_|.com
version 0.1
"""


def show_logo():
    print(LOGO)


def clip_url(img):
    try:
        return img.rpartition("/")[-1]
    except AttributeError:
        print("ValueError!")


def fetch_url(url):
    return requests.get(url).text


def get_images_from_page(url):
    html = fetch_url(url)
    soup = bs(html, "html.parser")
    try:
        for link in soup.find_all("div", {"id": "comic"}):
            for img in link.find_all("img", src=True):
                return "https:" + img["src"]
    except TypeError:
        print("Invalid or unavailable url!")


def save_image(img):
    comic_name = clip_url(img)
    print(f"Downloading: {comic_name}")
    f_name = SAVE_DIRECTORY / comic_name
    with requests.get(img, stream=True) as img, open(f_name, "wb") as output:
        copyfileobj(img.raw, output)


def make_dir():
    return os.makedirs(SAVE_DIRECTORY, exist_ok=True)


def get_xkcd():
    show_logo()
    make_dir()
    for page in range(2068, CURRENT_MAX_PAGE + 1):
        print(f"Fetching page {page} out of {CURRENT_MAX_PAGE}")
        save_image(get_images_from_page(f"{BASE_URL}{page}/"))


def main():
    get_xkcd()


if __name__ == '__main__':
    main()
