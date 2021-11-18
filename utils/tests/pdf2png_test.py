import os
import shutil
import unittest
import utils.pdf2png as p2p


def message_warning(x):
    print("Warning: ", x)


class UtilsTest(unittest.TestCase):

    def test_corrupt_file_error_fitz(self):
        file = os.path.join(os.path.dirname(__file__), "test_input", "Grundfosliterature-1073171.pdf")
        out_dir = os.path.join(os.path.dirname(__file__), "test_output")

        # with self.assertWarns(RuntimeWarning):
        # shutil.move(file, out_dir)
        message_warning("Corrupt file found.")


if __name__ == '__main__':
    unittest.main()
