import os
import random
from time import sleep
import requests

class Scraper:
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
    wsUtils = None

    def __init__(self, wsUtils):
        self.wsUtils = wsUtils

    def get_response_headers(self):
        index = self.read_index_from_file() + 1
        for x in range(index, self.MAX_SITES_TO_CHECK + index - 1):
            self.wsUtils.updateLinksScraped(x, self.MAX_SITES_TO_CHECK + index)
            link = self.PDF_DOMAIN + str(x) + self.FILETYPE
            read = requests.head(link)
            content_type = read.headers.get("content-type")
            print(f"{x}: Content-type = {content_type}")
            if content_type is None:
                self.invalid_links.add(link + "\n")
            elif content_type == "application/pdf":
                self.valid_links.add(link + "\n")
            if x % self.ITERATIONS_BEFORE_DELAY == 1:
                self.delay()
        self.safe_index(self.MAX_SITES_TO_CHECK + index - 1)

        return


    def delay(self):
        sleeptimer = random.uniform(self.MIN_SLEEP, self.MAX_SLEEP)
        print(f"Sleeping {sleeptimer} seconds")
        #sleep(sleeptimer)


    def safe_valid_links(self):
        file = open(self.PATH_TO_VALID_LINKS, "a")
        file.writelines(self.valid_links)
        file.close()


    def safe_invalid_links(self):
        file = open(self.PATH_TO_INVALID_LINKS, "a")
        file.writelines(self.invalid_links)
        file.close()


    def safe_index(self, index: int):
        file = open(self.PATH_TO_INDEXES_CHECKED, "w")
        file.write(str(index))
        file.close()


    def read_index_from_file(self):
        file = open(self.PATH_TO_INDEXES_CHECKED, "r")
        index = int(file.readline())
        file.close()
        return index
