import os
import unittest
import utils.pdf2png as p2p


class UtilsTest(unittest.TestCase):

    def test_corrupt_file_error_fitz(self):
        file = os.path.join(os.path.abspath(os.curdir), "test_input") + "/Grundfosliterature-1073171.pdf"
        out_dir = os.path.join(os.path.abspath(os.curdir), "test_output")

        with self.assertWarns(RuntimeWarning):
            p2p.convert_to_file(file, out_dir)


if __name__ == '__main__':
    unittest.main()
