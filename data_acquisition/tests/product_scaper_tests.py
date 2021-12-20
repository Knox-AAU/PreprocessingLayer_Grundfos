import unittest
import data_acquisition.product_name_scraper as ps
import os

DOMAIN = "https://www.manualslib.com/brand/grundfos/"
PATH_TO_PRODUCTS = (
    os.path.join(os.path.abspath(os.curdir), "scrapertestdata") + "/products.txt"
)


class TestProductScraper(unittest.TestCase):
    def test_amount_of_categories(self):
        # Get amount of categories currently:
        amount = ps.get_href_for_categories(DOMAIN)

        # Set current known categories, found by counting them manually
        current_amount = 59

        # Check if they are equal
        self.assertEqual(current_amount, len(amount))

    def test_save_to_file(self):
        # Create list of random strings
        strings = ["Hello\n", "World\n", "I\n", "Chocolate\n", "Bananas\n", "Bonanza\n"]

        # Clean file for satety measures
        open(PATH_TO_PRODUCTS, "w").close()

        # Save the list of strings
        ps.save_names_to_list(strings, PATH_TO_PRODUCTS)

        # Read the contents of the products file, saved before
        file = open(PATH_TO_PRODUCTS, "r")
        contents = file.readlines()
        file.close()

        # check if they are equal
        self.assertEqual(contents, strings)

    def test_amount_of_products(self):
        # Set the current total amount of working product names within all categories
        amount = 1687

        # Get all categories
        categories = ps.get_href_for_categories(DOMAIN)
        # Get all products within each category
        total_products = ps.get_product_names(categories)

        # See if they are equal
        self.assertEqual(len(total_products), amount)


if __name__ == "__main__":
    unittest.main()
