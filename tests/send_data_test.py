import os
import sys
import unittest

import requests

from config_data import config
import send_json
import segment as seg

class SendDataTest(unittest.TestCase):
    def test_pingServer(self):
        if (os.name == "nt"):
            response = os.system("ping -n 1 130.225.57.27")
        else:
            response = os.system("ping -c 1 130.225.57.27")
            
        self.assertEqual(response, 0)
        
    def test_legitEmptySchema(self):
        config["OUTPUT_FOLDER"] = os.path.join(os.getcwd(), "tests", "data", "emptyJsonValid")
        try:
            send_json.send_data()
        except requests.exceptions.HTTPError as e:
            self.fail(("Knowledge layer server returned unexpected HTTP response code.\n" +
                       "Test data send can be found in folder: " + config["OUTPUT_FOLDER"]))

if __name__ == '__main__':
    unittest.main()