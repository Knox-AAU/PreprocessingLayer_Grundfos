import os
import random
from time import sleep

import requests

FILETYPE = '.pdf'
DOMAIN = 'https://www.grundfos.com'
MAX_SITES_TO_CHECK = 100 #7000001 #7 million is chosen just to get a good sample size, however this process make time LONG time
ITERATIONS_BEFORE_DELAY = 20 #Choose whatever works so the API doensn't block the connections because of insane amount of pings
MIN_SLEEP = 10
MAX_SLEEP = 20
PDF_DOMAIN = "http://net.grundfos.com/Appl/ccmsservices/public/literature/filedata/Grundfosliterature-"
PATH_TO_INVALID_LINKS = os.path.join(os.path.abspath(os.curdir), "scraperdata") + "/invalid_links.txt"
PATH_TO_VALID_LINKS = os.path.join(os.path.abspath(os.curdir), "scraperdata") + "/downloadable_links.txt"
PATH_TO_INDEXES_CHECKED = os.path.join(os.path.abspath(os.curdir), "scraperdata") + "/checked_links.txt"

invalid_links = set()
valid_links = set()


def get_response_headers():
    index = read_index_from_file() + 1
    for x in range(index, MAX_SITES_TO_CHECK):
        link = PDF_DOMAIN + str(x) + FILETYPE
        read = requests.get(link)
        content_type = read.headers.get("content-type")
        print(f"{x}: Content-type = {content_type}")
        if content_type is None:
            invalid_links.add(link + "\n")
        elif content_type == "application/pdf":
            valid_links.add(link + "\n")
        if x % ITERATIONS_BEFORE_DELAY == 1:
            delay()
        if x == MAX_SITES_TO_CHECK - 1:
            safe_index(x)

    return


def delay():
    sleeptimer = random.uniform(MIN_SLEEP, MAX_SLEEP)
    print(f"Sleeping {sleeptimer} seconds")
    sleep(sleeptimer)


def safe_valid_links():
    file = open(PATH_TO_VALID_LINKS, "a")
    file.writelines(valid_links)
    file.close()


def safe_invalid_links():
    file = open(PATH_TO_INVALID_LINKS, "a")
    file.writelines(invalid_links)
    file.close()


def safe_index(index: int):
    file = open(PATH_TO_INDEXES_CHECKED, "w")
    file.write(str(index))
    file.close()


def read_index_from_file():
    file = open(PATH_TO_INDEXES_CHECKED, "r")
    index = int(file.readline())
    file.close()
    return index


if __name__ == "__main__":
    print("initiating the scraper")
    get_response_headers()
    safe_valid_links()
    safe_invalid_links()
