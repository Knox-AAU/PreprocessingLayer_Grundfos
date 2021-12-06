import os
import random
from time import sleep

import requests

FILETYPE = '.pdf'
DOMAIN = 'https://www.grundfos.com'
MAX_SITES_TO_CHECK = 100 #7000001 #7 million is chosen just to get a good sample size, however this process make time LONG time
ITERATIONS_BEFORE_DELAY = 100 #Choose whatever works so the API doensn't block the connections because of insane amount of pings
MIN_SLEEP = 10
MAX_SLEEP = 20
PDF_DOMAIN = "http://net.grundfos.com/Appl/ccmsservices/public/literature/filedata/Grundfosliterature-"
PATH_TO_INVALID_LINKS = os.path.join(os.path.abspath(os.curdir), "scraperdata") + "/invalid_links.txt"
PATH_TO_VALID_LINKS = os.path.join(os.path.abspath(os.curdir), "scraperdata") + "/downloadable_links.txt"
PATH_TO_INDEXES_CHECKED = os.path.join(os.path.abspath(os.curdir), "scraperdata") + "/checked_links.txt"

invalid_links = set()
valid_links = set()


def get_response_headers():
    index = read_index_from_file(PATH_TO_INDEXES_CHECKED) + 1
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
            safe_index(x, PATH_TO_INDEXES_CHECKED)

    return


def delay():
    sleeptimer = random.uniform(MIN_SLEEP, MAX_SLEEP)
    print(f"Sleeping {sleeptimer} seconds")
    sleep(sleeptimer)


def safe_valid_links(links, path):
    file = open(path, "a")
    file.writelines(links)
    file.close()


def safe_invalid_links(links, path):
    file = open(path, "a")
    file.writelines(links)
    file.close()


def safe_index(index: int, path):
    file = open(path, "w")
    file.write(str(index))
    file.close()


def read_index_from_file(path):
    file = open(path, "r")
    index = int(file.readline())
    file.close()
    return index


if __name__ == "__main__":
    print("initiating the scraper")
    get_response_headers()
    safe_valid_links(valid_links, PATH_TO_VALID_LINKS)
    safe_invalid_links(invalid_links, PATH_TO_INVALID_LINKS)
