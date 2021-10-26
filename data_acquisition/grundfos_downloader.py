"""
This module has functionality to download the provided Grundfos pdfs.
"""
import os
import argparse
import pathlib
import requests


DOMAIN = "https://www.grundfos.com"

def download_data(save_folder: str = "downloads"):
    """
    Downloads pdfs from the IOlinks.txt.
    """
    print("Downloading PDF files from grundfos website...")
    # Read all links
    file1 = open(os.path.join(pathlib.Path(__file__).parent.absolute(), 'ioilinks.txt'), 'r')
    lines = file1.readlines()

    # Check if a folder for pdf is made
    out_folder = os.path.join(os.getcwd() ,save_folder)
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    pdf_download_count = 0
    for line in lines:
        # Get a file name
        product_name = findfilename(line.rstrip("\n"))

        with open(os.path.join(out_folder, product_name), 'wb') as file:
            print("Downloading " + product_name + "...")
            response = requests.get(line)
            file.write(response.content)
            print(product_name + " saved to " + os.path.join(out_folder, product_name))
            pdf_download_count += 1

    print(str(pdf_download_count) + " PDF files downloaded.")


def findfilename(string):
    """
    Parses a link to get the name of the file.
    """
    dirs = string.split('/')
    return dirs[len(dirs)-1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", action="store", help="Custom output folder for the downloaded files.")
    argv = parser.parse_args()

    download_data(argv.output)
