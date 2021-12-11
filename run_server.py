"""
Runs websockets, making the program accessable through the UI.
"""

import signal
import copy
from threading import Thread, Event
import time
import data_acquisition.downloader as downloader
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json
from data_acquisition.scraper import Scraper
from defaultProgramArguments import defaultArguments, defaultEnviromentVariables
from segment import Segmentation
from send_json import send_data
import config_data
from config_data import config
from ws_states import *

exit_event = Event()

# List of websocket clients
wsClients = []
wsUtils = None


def wsRunner():
    server = SimpleWebSocketServer("localhost", 1337, WsHandleClients)
    print("Running WS server, and waiting for commands...")

    while exit_event.is_set() == False:
        server.serveonce()
        time.sleep(0.1)

    print("Closing websocket server...")
    server.close()


class WsHandleClients(WebSocket):
    def handleMessage(self):
        print("Message recived from ws!: " + (self.data or ""))
        wsUtils.handleReceivedData(self.data)

    def handleConnected(self):
        wsClients.append(self)
        wsUtils.sendInitzDataOnConenction(self)

    def handleClose(self):
        wsClients.remove(self)


class WsUtils:
    """
    Methods for sending data to the UI
    """

    _jsonBaseObject = {
        "source": "grundfoss_preprocessing",
        "type": "updateStatus",
        "contents": {},
    }

    numberOfPDFs = 0
    numberOfPages = 0
    currentPdf = 0
    filename = ""
    state = State.IDLE
    argv = None

    def __init__(self, argv):
        self.argv = argv

    def setState(self, newState: State):
        self.state = newState
        data = copy.deepcopy(self._jsonBaseObject)

        data["contents"]["setState"] = newState.name
        self.sendToAll(data)

    def updateCurrentPdf(self, pageNumb, fileName):
        self.currentPdf = pageNumb
        self.fileName = fileName

        data = copy.deepcopy(self._jsonBaseObject)
        data["contents"]["currentPdf"] = pageNumb
        data["contents"]["fileName"] = fileName
        self.sendToAll(data)

    def updatePageNumbers(self, page, pages):
        data = copy.deepcopy(self._jsonBaseObject)
        data["contents"]["page"] = page
        data["contents"]["pages"] = pages
        self.sendToAll(data)

    def sendInitzDataOnConenction(self, client):
        data = copy.deepcopy(self._jsonBaseObject)
        data["contents"]["setState"] = self.state.name
        if self.state == State.GENERATING_IMAGES:
            data["contents"]["imagePages"] = self.numberOfPages
        elif self.state == State.PROCESSING:
            data["contents"]["numberOfPDFs"] = self.numberOfPDFs
            data["contents"]["currentPdf"] = self.currentPdf
            data["contents"]["fileName"] = self.fileName
        client.sendMessage(self.encodeToJson(data))

    def updateNumberOfPdfFiles(self):
        data = copy.deepcopy(self._jsonBaseObject)
        data["contents"]["numberOfPDFs"] = self.numberOfPDFs
        self.sendToAll(data)

    def sendToAll(self, data):
        json = self.encodeToJson(data)
        for client in wsClients:
            client.sendMessage(json)

    def updateImagePageNumbers(self, imagePage, imagePages):
        data = copy.deepcopy(self._jsonBaseObject)
        data["contents"]["imagePage"] = imagePage
        data["contents"]["imagePages"] = imagePages
        self.sendToAll(data)

    def updateLinksScraped(self, currentScrapeLink, totalScrapeLinks):
        data = copy.deepcopy(self._jsonBaseObject)
        data["contents"]["currentScrapeLink"] = currentScrapeLink
        data["contents"]["totalScrapeLinks"] = totalScrapeLinks
        self.sendToAll(data)

    def updateFilesDownloaded(
        self, currentDownloadFile, currentDownloadFileName, totalDownloadFiles
    ):
        data = copy.deepcopy(self._jsonBaseObject)
        data["contents"]["currentDownloadFile"] = currentDownloadFile
        data["contents"]["fileName"] = currentDownloadFileName
        data["contents"]["totalDownloadFiles"] = totalDownloadFiles
        self.sendToAll(data)

    def updateJsonSent(self, currentJsonFile, currentJsonFileName, totalJsonFiles):
        data = copy.deepcopy(self._jsonBaseObject)
        data["contents"]["currentJsonFile"] = currentJsonFile
        data["contents"]["currentJsonFileName"] = currentJsonFileName
        data["contents"]["totalJsonFiles"] = totalJsonFiles
        self.sendToAll(data)

    def encodeToJson(self, data):
        return json.dumps(data)

    def handleReceivedData(self, jsonData):
        if self.state == State.IDLE or self.state == State.FINISHED:
            try:
                data = json.loads(jsonData)
                if data["type"] == "executeCommands":
                    rcThread = Thread(target=self.runCommands, args=(data["contents"],))
                    rcThread.start()
            except ValueError as ve:
                print("Could not parse JSON data from client.")
            except AttributeError as ae:
                print("JSON data from client has invalid structure.")

    def runCommands(self, commands):
        for command in commands:
            print(command)
            if command["commandType"] == Commands.SCRAPE.name:
                self.setState(State.SCRAPING)
                scraper = Scraper(wsUtils)
                scraper.get_response_headers()
                scraper.safe_valid_links()
                scraper.safe_invalid_links()
                self.setState(State.DOWNLOADING)
                downloader.download_data(config["INPUT_FOLDER"], wsUtils)
            elif command["commandType"] == Commands.PROCESS.name:
                Segmentation(self.argv, wsUtils)
            elif command["commandType"] == Commands.SEND.name:
                self.setState(State.SENDING)
                send_data(wsUtils)
            else:
                print("Command received but not recognised: " + command.commandType)
        self.setState(State.FINISHED)


def signal_handler(signum, frame):
    exit_event.set()


if __name__ == "__main__":
    argv = defaultArguments(
        "Run ws server for UI, and execute commands received."
    ).parse_args()
    defaultEnviromentVariables(argv, config_data)
    config_data.check_config(["GRUNDFOS_INPUT_FOLDER", "GRUNDFOS_OUTPUT_FOLDER"])

    wsUtils = WsUtils(argv)
    # Handles ctrl+c (interupting the prgram)
    signal.signal(signal.SIGINT, signal_handler)
    ws_thread = Thread(target=wsRunner)
    ws_thread.start()
    while ws_thread.is_alive():
        time.sleep(0.1)
