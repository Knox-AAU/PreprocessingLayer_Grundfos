import os
import unittest
import data_acquisition.scraper as scaper

PATH_TO_INVALID_LINKS = (
    os.path.join(os.path.abspath(os.curdir), "scrapertestdata") + "/invalid_links.txt"
)
PATH_TO_VALID_LINKS = (
    os.path.join(os.path.abspath(os.curdir), "scrapertestdata")
    + "/downloadable_links.txt"
)
PATH_TO_INDEXES_CHECKED = (
    os.path.join(os.path.abspath(os.curdir), "scrapertestdata") + "/checked_links.txt"
)


class ScraperTests(unittest.TestCase):
    def test_write_to_file(self):
        # Test input
        test_string1 = "Hello World!"
        test_string2 = "Hercules1"
        test_int = 45

        # Clean the files for current content
        file = open(PATH_TO_VALID_LINKS, "w").close()
        file = open(PATH_TO_INVALID_LINKS, "w").close()
        file = open(PATH_TO_INDEXES_CHECKED, "w")
        file.write("0")
        file.close()

        # Save test inputs
        scaper.safe_valid_links(test_string1, PATH_TO_VALID_LINKS)
        scaper.safe_invalid_links(test_string2, PATH_TO_INVALID_LINKS)
        scaper.safe_index(test_int, PATH_TO_INDEXES_CHECKED)

        # Read the files new content
        file = open(PATH_TO_VALID_LINKS, "r")
        result_string1 = file.read()
        file.close()
        file = open(PATH_TO_INVALID_LINKS, "r")
        result_string2 = file.read()
        file.close()
        file = open(PATH_TO_INDEXES_CHECKED, "r")
        result_int = int(file.read())
        file.close()

        print(result_string1)
        print(result_string2)
        print(result_int)

        # Test if they are the same
        self.assertEqual(test_string1, result_string1)
        self.assertEqual(test_string2, result_string2)
        self.assertEqual(test_int, result_int)

    def test_read_write_indexes_integration_test(self):
        test_int = 34
        scaper.safe_index(test_int, PATH_TO_INDEXES_CHECKED)
        result_int = int(scaper.read_index_from_file(PATH_TO_INDEXES_CHECKED))
        self.assertEqual(test_int, result_int)


if __name__ == "__main__":
    unittest.main()
