import os
import platform
import unittest

import config_data
import utils.pdf2png as p2p


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

if __name__ == '__main__':
    unittest.main()
