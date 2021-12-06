"""
This module has functionality to download the provided Grundfos pdfs, from ioilinks.txt
"""
import os
import argparse
import pathlib
import requests
from segment import WsUtils

DOMAIN = "https://www.grundfos.com"


def download_data(save_folder, wsUtils: WsUtils):
    """
    Downloads pdfs from the IOlinks.txt.
    """
    print("Downloading PDF files from grundfos website...")
    # Read all links
    downloadable_links = open(
        os.path.join(
            pathlib.Path(__file__).parent.absolute(),
            "scraperdata",
            "downloadable_links.txt",
        ),
        "r",
    )
    downloaded_links = open(
        os.path.join(
            pathlib.Path(__file__).parent.absolute(),
            "scraperdata",
            "downloaded_links.txt",
        ),
        "a",
    )
    lines = downloadable_links.readlines()
    # Check if a folder for pdf is made
    out_folder = os.path.join(save_folder)
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    pdf_download_count = 0
    for line in lines:
        # Get a file name
        product_name = findfilename(line.rstrip("\n"))

        wsUtils.updateFilesDownloaded(pdf_download_count + 1, product_name, len(lines))
        with open(os.path.join(out_folder, product_name), "wb") as file:
            print("Downloading " + product_name + "...")
            response = requests.get(line)
            file.write(response.content)
            print(product_name + " saved to " + os.path.join(out_folder, product_name))
            pdf_download_count += 1

    downloaded_links.writelines(lines)
    downloaded_links.close()
    downloadable_links.close()
    # downloadable_links.truncate(0)
    print(str(pdf_download_count) + " PDF files downloaded.")


def findfilename(string):
    """
    Parses a link to get the name of the file.
    """
    dirs = string.split("/")
    return dirs[len(dirs) - 1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="Custom output folder for the downloaded files.",
    )
    argv = parser.parse_args()

    download_data(argv.output)
