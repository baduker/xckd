#!/usr/bin/python3

import os
import requests


from bs4 import BeautifulSoup as bs
from pathlib import Path
from shutil import copyfileobj


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

version: 0.2 
"""


def show_logo():
    print(LOGO)


def clip_url(img):
    return img.rpartition("/")[-1]


def fetch_url(url):
    return requests.get(url).text


def get_current_comic_count():
    html = fetch_url(ARCHIVE)
    soup = bs(html, "html.parser")
    hrefs = []
    for link in soup.find_all("div", class_="box"):
        for br in link.find_all("a"):
            hrefs.append(br["href"])
    return int(hrefs[0].strip("/"))


def get_images_from_page(url):
    html = fetch_url(url)
    soup = bs(html, "html.parser")
    for link in soup.find_all("div", {"id": "comic"}):
        for img in link.find_all("img", src=True):
            return "https:" + img["src"]


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
    latest_comic = get_current_comic_count()
    for page in range(1, latest_comic + 1):
        print(f"Fetching page {page} out of {latest_comic}")
        save_image(get_images_from_page(f"{BASE_URL}{page}/"))


def main():
    get_xkcd()


if __name__ == '__main__':
    main()
