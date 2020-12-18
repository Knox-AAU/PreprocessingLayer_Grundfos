"""
This module provides functionality to segment pdf documents.
"""

import os
import shutil
import argparse
import copy
import cv2
import time
import concurrent.futures as cf
import IO_handler
from text_analyzer import TextAnalyser
import data_acquisition.grundfos_downloader as downloader
import miner
import classification.infer as mi
import utils.pdf2png as pdf2png
import utils.extract_area as extract_area
import datastructure.datastructure as datastructures
import IO_wrapper.manual_wrapper as wrapper

def segment_documents(args: str):
    """
    Does document segmentation of a pdf file and produces a json file with the information found.
    """
    tmp_folder = os.path.join(args.output, "tmp")
    IO_handler.folder_prep(args.output, args.clean)
    pdf2png.multi_convert_dir_to_files(args.input, os.path.join(tmp_folder, 'images'))  

    for file in os.listdir(args.input):
        if file.endswith('.pdf'):
            try:
                
                segment_document(file, args)
            except Exception as ex:
                #The file loaded was probably not a pdf and cant be segmented (with pdfminer)
                try:
                    print(ex)
                except:
                    pass

    if args.temporary is False:
        shutil.rmtree(tmp_folder)

def segment_document(file: str, args):
    """
    Segments a pdf document
    """
    schema_path = args.schema
    output_path = os.path.join(os.getcwd(), args.output, os.path.basename(file).replace(".pdf", ""))
    os.mkdir(output_path)

    #Create output folders
    os.mkdir(os.path.join(output_path, "tables"))
    os.mkdir(os.path.join(output_path, "images"))

    textline_pages = []
    pages = []
    current_pdf = miner.PDF_file(file, args)
    for page in current_pdf.pages:
        miner.search_page(page, args)
        miner.flip_y_coordinates(page)
        if (len(page.LTRectLineList) < 10000 and len(page.LTLineList) < 10000):
            #Only pages without a COLLOSAL amount of lines will be grouped. 
            #Otherwise the segmentation will take too long.
            miner.look_through_LTRectLine_list(page, args)
        image_path = os.path.join(args.output, "tmp", 'images', page.image_name)
        mined_page = miner.make_page(page)

        if args.machine is True:
            infered_page = infer_page(image_path, args.accuracy)
            result_page = merge_pages(mined_page, infered_page)
        else:
            result_page = mined_page
        
        miner.remove_text_within(page, [element.coordinates for element in result_page.images])
        miner.remove_text_within(page, [element.coordinates for element in result_page.tables])

        remove_duplicates_from_list(result_page.images)
        remove_duplicates_from_list(result_page.tables)
        produce_data_from_coords(result_page, image_path, output_path)
        pages.append(result_page)

        textline_pages.append([element.text_Line_Element for element in page.LTTextLineList])

    text_analyser = TextAnalyser(textline_pages)
    analyzed_text = text_analyser.segment_text()

    #Create output
    wrapper.create_output(analyzed_text, pages, current_pdf.file_name, schema_path, output_path)



def infer_page(image_path: str, min_score: float = 0.7) -> datastructures.Page:
    """
    Acquires tables and figures from MI-inference of documents.
    """
    #TODO: Make split more unique, so that files that naturally include "_page" do not fail
    page_data = datastructures.Page(int(os.path.basename(image_path).split("_page")[1].replace('.png','')))
    image = cv2.imread(image_path)
    prediction = mi.infer_image_from_matrix(image)

    for pred in prediction:
        for idx, mask in enumerate(pred['masks']):
            label = mi.CATEGORIES2LABELS[pred["labels"][idx].item()]

            if pred['scores'][idx].item() < min_score:
                continue
            area = convert2coords(image, list(map(int, pred["boxes"][idx].tolist())))
            #score = pred["scores"][idx].item()

            if label == "table":
                table = datastructures.TableSegment(area)
                page_data.tables.append(table)
            elif label == "figure":
                figure = datastructures.ImageSegment(area)
                page_data.images.append(figure)
            else:
                continue

            image = cv2.imread(image_path)
            extract_area.extract_area_from_matrix(image, image_path.split(".png")[0] + label + str(idx) + ".png", area)

    return page_data

def convert2coords(image, area: list) -> datastructures.Coordinates:
    """
    Converts coordinates from MI-inference format to fit original image format.
    """
    rat = image.shape[0] / 1300
    return datastructures.Coordinates(int(area[0] * rat), int(area[1] * rat),
                                      int(area[2] * rat), int(area[3] * rat))

def merge_pages(page1: datastructures.Page, page2: datastructures.Page) -> datastructures.Page:
    """
    Merges the contents of two page datastructures into one.
    """
    if page1.page_number != page2.page_number:
        raise Exception("Pages must have the same page-number.")

    # Copies pages to not delete any of the original data
    page1_cpy = copy.deepcopy(page1)
    page2_cpy = copy.deepcopy(page2)
    result = datastructures.Page(page1.page_number)

    result.add_from_page(page1_cpy)
    result.add_from_page(page2_cpy)
    return result

def remove_duplicates_from_list(list1: list):
    """
    Removes elements that reside in other elements.
    """
    threshold = 30
    for object1 in list1:
            for object2 in list1:
                if(object1 != object2):
                    #Checks if object 2 is within object 1:
                    if (object2.coordinates.x0 >= object1.coordinates.x0 - threshold and
                        object2.coordinates.x1 <= object1.coordinates.x1 + threshold and
                        object2.coordinates.y0 >= object1.coordinates.y0 - threshold and
                        object2.coordinates.y1 <= object1.coordinates.y1 + threshold):
                        list1.remove(object2)

def produce_data_from_coords(page, image_path, output_path):
    """
    Produces matrixes that represent seperate images for all tables and figures on the page.
    """
    table_list_copy = copy.copy(page.tables)
    image_list_copy = copy.copy(page.images)

    area_treshold = 120 * 120
    image = cv2.imread(image_path)
    for table_number in range(len(table_list_copy)):
        if table_list_copy[table_number].coordinates.area() > area_treshold and ((table_list_copy[table_number].coordinates.is_negative() is False)):
            try: #TODO: Finish try-excepts
                table_list_copy[table_number].path = os.path.join(output_path, "tables", os.path.basename(image_path).replace(".png", "_table" + str(table_number) + ".png"))
                extract_area.extract_area_from_matrix(image, table_list_copy[table_number].path, table_list_copy[table_number].coordinates)
            except Exception as x:
                print(x)
        else:
            page.tables.remove(table_list_copy[table_number])
    for image_number in range(len(image_list_copy)):
        if (image_list_copy[image_number].coordinates.area() > area_treshold) and (image_list_copy[image_number].coordinates.is_negative() is False):
            try:
                image_list_copy[image_number].path = os.path.join(output_path, "images",os.path.basename(image_path).replace(".png", "_image" + str(image_number) + ".png"))
                extract_area.extract_area_from_matrix(image, image_list_copy[image_number].path, image_list_copy[image_number].coordinates)
            except Exception as x:
                print(x)
        else:
            page.images.remove(image_list_copy[image_number])


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Segments pdf documents.")
    argparser.add_argument("input", type=str, action="store", metavar="INPUT", help="Path to input folder.")
    argparser.add_argument("output",type=str, action="store", metavar="OUTPUT", help="Path to output folder.")
    argparser.add_argument("-a", "--accuracy", type=float, default=0.7, metavar="A", help="Minimum threshold for the prediction accuracy. Value between 0 to 1.")
    argparser.add_argument("-m", "--machine", action="store_true", help="Enable machine intelligence crossreferencing.") #NOTE: Could be merged with accuracy arg
    argparser.add_argument("-t", "--temporary", action="store_true", default=False, help="Keep temporary files")
    argparser.add_argument("-c", "--clean", action="store_true", default=False, help="Clear output folder before running.")
    argparser.add_argument("-s", "--schema", type=str, action="store", default="/schema/manuals_v1.1.schema.json", help="Path to json schema.")
    argparser.add_argument("-d", "--download", action="store_true", default=False, help="Downloads Grundfos data to input folder.")
    argv = argparser.parse_args()

    if argv.download is True:
        downloader.download_data(argv.input)

    segment_documents(argv)