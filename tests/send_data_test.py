import os
import sys
import unittest

from config_data import config
import send_json
import segment as seg

class SendDataTest(unittest.TestCase):
    def test_pingserver(self):
        if (os.name == "nt"):
            response = os.system("ping -n 1 130.225.57.27")
        else:
            response = os.system("ping -c 1 130.225.57.27")
            
        self.assertEqual(response, 0)
        
    #def test_leigtemptySchema(self):
    #    config["OUTPUT_FOLDER"] = "./data/emptyJsonValid/"
    #    send_json.send_data()
    #    self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()