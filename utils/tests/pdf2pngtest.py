import os
import platform
import unittest

import config_data
import utils.pdf2png as p2p
from config_data import config


class UtilsTest(unittest.TestCase):

    def test_corrupt_file_error_fitz(self):
        file = os.path.join(os.path.abspath(os.curdir), "test_input") + "/Grundfosliterature-1073171.pdf"
        out_dir = os.path.join(os.path.abspath(os.curdir), "test_output")

        os.environ["GRUNDFOS_INVALID_INPUT_FOLDER"] = str(os.path.join(os.path.abspath(os.curdir), "test_invalid"))
        config_data.set_config_data_from_envs()

        with self.assertWarns(RuntimeWarning):
            p2p.convert_to_file(file, out_dir)

    def test_corrupt_ghostscript(self):
        file = os.path.join(os.path.abspath(os.curdir), "test_input")
        out_dir = os.path.join(os.path.abspath(os.curdir), "test_output")

        os.environ["GRUNDFOS_INVALID_INPUT_FOLDER"] = str(os.path.join(os.path.abspath(os.curdir), "test_invalid"))
        config_data.set_config_data_from_envs()

        with self.assertWarns(RuntimeWarning):
            p2p.multi_convert_dir_to_files(file, out_dir)


    def test_write_corrupt_to_file(self):
        os.environ["GRUNDFOS_INVALID_INPUT_FOLDER"] = str(os.path.join(os.path.abspath(os.curdir), "test_invalid"))
        config_data.set_config_data_from_envs()
        input = "CORRUPT_PDF_NAME_EXAMPLE.pdf"
        files = []
        files.append(input)

        p2p.write_invalid_pdf_list(files)
        file = open(os.path.join(config["INVALID_INPUT_FOLDER"], "invalids.txt"),"r")
        output = file.read()
        file.close()
        self.assertEqual(input + " \n", output)



if __name__ == '__main__':
    unittest.main()
