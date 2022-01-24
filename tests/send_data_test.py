from logging import exception
import os
import sys
import unittest

import requests

from config_data import config
import send_json
import segment as seg

class WsUtilsTestMock:
    def updateJsonSent(self, currentJsonFile, currentJsonFileName, totalJsonFiles):
        pass

class SendDataTest(unittest.TestCase):
    def test_pingServer(self):
        if os.name == "nt":
            response = os.system("ping -n 1 130.225.57.27")
        else:
            response = os.system("ping -c 1 130.225.57.27")

        self.assertEqual(response, 0)

    def test_legitEmptySchema(self):
        config["OUTPUT_FOLDER"] = os.path.join(
            os.getcwd(), "tests", "data", "emptyJsonValid"
        )
        try:
            send_json.send_data(WsUtilsTestMock(), "http://127.0.0.1:8000/uploadJsonDoc/")
        except requests.exceptions.HTTPError:
            self.fail(self.failDataToKnowledgeLayerMsg())

    def test_invalidEmptySchema(self):
        config["OUTPUT_FOLDER"] = os.path.join(
            os.getcwd(), "tests", "data", "jsonInvalid"
        )
        with self.assertRaises(requests.exceptions.HTTPError):
            send_json.send_data(WsUtilsTestMock(), "http://127.0.0.1:8000/uploadJsonDoc/")

    def failDataToKnowledgeLayerMsg(self):
        return (
            "Knowledge layer server returned unexpected HTTP response code.\n"
            + "Test data send can be found in folder: "
            + config["OUTPUT_FOLDER"]
        )


if __name__ == "__main__":
    unittest.main()
