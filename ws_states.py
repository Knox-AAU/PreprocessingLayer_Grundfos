from enum import Enum

class State(Enum):
    IDLE = 0
    SCRAPING = 1
    DOWNLOADING = 2
    GENERATING_IMAGES = 3
    PROCESSING = 4
    SENDING = 5
    FINISHED = 6

class Commands(Enum):
    SCRAPE = 0
    PROCESS = 1
    SEND = 2