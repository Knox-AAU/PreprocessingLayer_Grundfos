"""
This module allows conversion of PDF files to PNG files.
"""
import os
import argparse
import concurrent.futures as cf
import platform
import shutil
import sys
import warnings as warn

import fitz
import ghostscript
import numpy as np
from PIL import Image
from config_data import config


ZOOM = 3
VERBOSE = True


def move_invalid_files_windows(files: list):
    for file in files:
        shutil.move(file, config["INVALID_INPUT_FOLDER"])
        print(f"Moved {file} into the invalid folder")

    print("Finishing moving corrupt files into another directory")


def convert_to_file(file: str, out_dir: str):
    """
    Converts a PDF file and writes each page as a PNG image in the 'out_dir' directory.
    """
    print("Converting " + file + "...")
    mat = fitz.Matrix(ZOOM, ZOOM)
    invalid_files = []
    # Open image and get page count
    try:
        doc = fitz.open(file)
        number_of_pages = doc.pageCount

        # Convert each page to an image
        for page_number in range(number_of_pages):
            page = doc.loadPage(page_number)
            pix = page.getPixmap(matrix=mat)
            output_name = os.path.basename(file).replace(".pdf", "") + "_page" + str(page_number + 1) + ".png"
            pix.writePNG(os.path.join(out_dir, output_name))

    except Exception:
        warn.warn("Corrupt file caught by fitz", RuntimeWarning)
        if str(platform.system()).upper() == "WINDOWS":
            print("Added file to list for later removal.")
            invalid_files.append(file)
        else:
            print("Moved file to the invalid folder.")
            shutil.move(file, config["INVALID_INPUT_FOLDER"])

    move_invalid_files_windows(invalid_files)

    if VERBOSE is True:
        print("Finished converting " + file + ".")

def convert_dir_to_files(in_dir: str, out_dir: str):
    """
    Convert a directory of PDF files and writes each page as a PNG image in the 'out_dir' directory.
    """

    for file in os.listdir(in_dir):
        if file.endswith(".pdf"):
            convert_to_file(os.path.join(in_dir, file), out_dir)

def multi_convert_dir_to_files(in_dir: str, out_dir: str):
    """
    Convert a directory of PDF files and writes each page as a PNG image in the 'out_dir' directory.
    Multi-processed.
    """
    # Go through every file in the input dir and append to list.
    invalid_files = []
    files = []
    out_dirs = []
    for file in os.listdir(in_dir):
        if file.endswith(".pdf"):
            try:
                ar = ["-sDEVICE=pdfwrite", "-dPDFSETTINGS=/prepress", "-dQUIET", "-dBATCH", "-dNOPAUSE",
                      "-dPDFSETTINGS=/printer", "-sOutputFile=" + in_dir + "/" + file, "-dPDFSETTINGS=/prepress", in_dir + "/" + file]
                ghostscript.Ghostscript(*ar)
                files.append(os.path.join(in_dir, file))
                out_dirs.append(out_dir)
            except Exception:
                warn.warn("Corruptness caught by GhostScript", RuntimeWarning)
                if str(platform.system()).upper() == "WINDOWS":
                    print("Added file to list for later removal.")
                    invalid_files.append(os.path.join(in_dir, file))
                else:
                    print("Moved file to the invalid folder.")
                    shutil.move(in_dir + "/" + file, config["INVALID_INPUT_FOLDER"])

    move_invalid_files_windows(invalid_files)

    with cf.ProcessPoolExecutor() as executor:
        executor.map(convert_to_file, files, out_dirs)

def convert_to_matrix(file: str):
    """
    Converts a PDF file to image matrices and return a list containing a matrix for each page.
    """
    print("Converting " + file + " to image matrices...")
    mat = fitz.Matrix(ZOOM, ZOOM)

    # Open image and get page count
    doc = fitz.open(file)
    number_of_pages = doc.pageCount

    result = []

    # Convert each page to an image
    for page_number in range(number_of_pages):
        page = doc.loadPage(page_number)

        #Convert from pdf to PIL format
        pix = page.getPixmap(matrix=mat)
        pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        #C Convert from PIL format to cv2 format
        cv2_image = np.array(pil_image)
        result.append(cv2_image)

    print("Finished converting " + file + ".")
    return result

# TODO: List could be substituted with dictionary and have filenames as keys
def convert_dir_to_matrices(in_dir: str):
    """
    Convert a directory of PDF files to matrices. Returns a list of lists containing matrices.
    """
    result = []
    for file in os.listdir(in_dir):
        if file.endswith(".pdf"):
            result.append(convert_to_matrix(file))

    return result


if __name__ == "__main__":
    # Setup command-line arguments
    parser = argparse.ArgumentParser(description="Convert pdf files to png images.")
    parser.add_argument("input", metavar = "IN", type = str, help = "Path the input folder.")
    parser.add_argument("output", metavar = "OUT", type = str, help = "Path to output folder.")
    parser.add_argument("-z", "--zoom", metavar = "N", type = int, default = 3, help = "Zoom of the PDF conversion.")
    parser.add_argument("-v", "--verbose", action = "store_true", default = False, help = "Print more information.")
    parser.add_argument("-m", "--multithreaded", action = "store_true", default = False, help = "Multithread the conversion process. Only works for folders.")
    argv = parser.parse_args()

    ZOOM = argv.zoom
    VERBOSE = argv.verbose

    # Make sure that output exists. If not, create the dir.
    if not os.path.isdir(argv.output):
        print("Output directory must be a correct existing path.")

    if VERBOSE is True:
        print("Creating PNG files...")

    if os.path.isfile(argv.input):
        if argv.input.endswith(".pdf"):
            convert_to_file(argv.input, argv.output)
        else:
            print("Input file must be a PDF file.")
    elif os.path.isdir(argv.input):
        # Print the number of files to be converted.
        num_files = len([f for f in os.listdir(argv.input)if os.path.isfile(os.path.join(argv.input, f))])
        if VERBOSE is True:
            print("Converting " + str(num_files) + " PDF files...")

        # Convert all pdfs.
        if argv.multithreaded is True:
            multi_convert_dir_to_files(argv.input, argv.output)
        else:
            convert_dir_to_files(argv.input, argv.output)
        print("Finished converting" + str(num_files) + " PDF files.")
    else:
        print("Could not find input file/directory.")
        exit()

    # Print number of files created.
    num_files = len([f for f in os.listdir(argv.output)if os.path.isfile(os.path.join(argv.output, f))])
    if VERBOSE is True:
        print("Created " + str(num_files) + " PNG files.")
    exit()
