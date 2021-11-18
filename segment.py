"""
This module provides functionality to segment pdf documents.
This is the main script of the project, that can:
Download pdf-files, segment the pdf files, and generate output.
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
import time
import multiprocessing
import shutil
import config_data
from config_data import config
import warnings as warn
from PyPDF2 import PdfFileReader
import psutil
import fitz
import utils.ghostscript_module as gs
import gc
import traceback

def checkFile(fullfile, invalid_files):
    for file in invalid_files:
        if fullfile == file:
            return False

    with open(fullfile, 'rb') as f:
        try:
            pdf = PdfFileReader(f)
            info = pdf.getDocumentInfo()
            if info:
                return True
            else:
                return False
        except:
            return False


def segment_documents(args: str):
    """
    Does document segmentation of all pdf files in the input folder,
    and produces JSON files with the information found.
    """
    print("Beginning segmentation of " + str(len(os.listdir(config["INPUT_FOLDER"]))) + " documents...")
    tmp_folder = os.path.join(config["OUTPUT_FOLDER"], "tmp")
    IO_handler.folder_prep(config["OUTPUT_FOLDER"], args.clean)
    invalid_files = gs.run_ghostscript(config["INPUT_FOLDER"])
    pdf2png.multi_convert_dir_to_files(config["INPUT_FOLDER"], os.path.join(tmp_folder, 'images'))

    for file in os.listdir(config["INPUT_FOLDER"]):
        if file.endswith('.pdf'):
            try:
                output_path = os.path.join(config["OUTPUT_FOLDER"],
                                           os.path.basename(file).replace(".pdf", ""))
                if checkFile(os.path.join(config["INPUT_FOLDER"], file), invalid_files) is False:
                    os.remove(file)
                    print("WARNING: PDF file deleted.")
                    break
                
                print("\nGathering meta data...")

                doc = fitz.open(os.path.join(config["INPUT_FOLDER"], file))
                pages = doc.pageCount
                del doc

                gc.collect()

                print("STARTING THREAD")
                seg_doc_process = multiprocessing.Process(target=segment_document, name="Segment_document", args=(
                    file, args, output_path))  # creates new process that segments file
                seg_doc_process.start()

                estimated_per_page = float(20)  # max time to process each page
                print("PDF Pages: " + str(pages))
                max_time = time.time() + (estimated_per_page * float(pages))

                while True:
                    if not seg_doc_process.is_alive():
                        print("Thread done!")
                        seg_doc_process.terminate()
                        seg_doc_process.close()
                        break

                    time.sleep(0.1)  # how often to check timer
                    if (time.time() > max_time):
                        seg_doc_process.terminate()
                        seg_doc_process.close()
                        print("Process: " + file + " terminated due to excessive time")
                        #warn.warn(f"Process: {file} terminated due to excessive time", UserWarning)
                        shutil.rmtree(output_path)
                    
                    # Kills process if memory usage is high
                    virtual = psutil.virtual_memory()
                    if (virtual.percent > 90):
                        seg_doc_process.terminate()
                        seg_doc_process.close()
                        print("Memory usage above 90%. PDF file extraction killed")

            except Exception as ex:
                # The file loaded was probably not a pdf and cant be segmented (with pdfminer)
                # This except may be obsolete and redundant in the overall process
                traceback.print_exc()
                print(file + " could not be opened and has been skipped!")
                
                try:
                    seg_doc_process.terminate()
                    seg_doc_process.close()

                    shutil.rmtree(output_path)
                except:
                    pass
            
            gc.collect()

    print("\nALL pdf files DONE :DDDD")

    if args.temporary is False:
        shutil.rmtree(tmp_folder)

def segment_document(file: str, args, output_path):
    """
    Segments a pdf document
    """
    # Has to run every time, as it's from another task, in case of environment variables not being set
    miner.initz_paths(args)
    print("Beginning segmentation of " + file + "...")
    schema_path = args.schema
    os.mkdir(output_path)

    # Create output folders
    if not os.path.exists(os.path.join(output_path, "tables")):
        os.mkdir(os.path.join(output_path, "tables"))
    if not os.path.exists(os.path.join(output_path, "images")):
        os.mkdir(os.path.join(output_path, "images"))

    # Check if folders are created

    textline_pages = []
    pages = []
    current_pdf = miner.PDF_file(file, args)

    for page in current_pdf.pages:
        miner.search_page(page, args)
        miner.flip_y_coordinates(page)
        if (len(page.LTRectLineList) < 10000 and len(page.LTLineList) < 10000):
            # Only pages without a COLOSSAL amount of lines will be grouped.
            # Otherwise the segmentation will take too long.
            # Consider writing a test if a PDF ever give an error on this
            miner.look_through_LTRectLine_list(page, args)
        else:
            print("PDF contains a page with way to many lines (above 10000)")
        image_path = os.path.join(config["OUTPUT_FOLDER"], "tmp", 'images', page.image_name)
        mined_page = miner.make_page(page)

        if args.machine is True:
            # Test whether or not it runs as expected (needs MI Fix)
            inferred_page = infer_page(image_path, args.accuracy)
            result_page = merge_pages(mined_page, inferred_page)
        else:
            result_page = mined_page

        miner.remove_text_within(page, [element.coordinates for element in result_page.images])
        miner.remove_text_within(page, [element.coordinates for element in result_page.tables])

        if args.machine is True:
            remove_duplicates_from_list(result_page.images)
            remove_duplicates_from_list(result_page.tables)
        
        produce_data_from_coords(result_page, image_path, output_path)
        pages.append(result_page)

        textline_pages.append([element.text_Line_Element for element in page.LTTextLineList])

    text_analyser = TextAnalyser(textline_pages)
    analyzed_text = text_analyser.segment_text()
    analyzed_text.OriginPath = os.path.join(config["INPUT_FOLDER"], file)

    # Create output
    wrapper.create_output(analyzed_text, pages, current_pdf.file_name, schema_path, output_path)
    print("Finished extracting.")

def infer_page(image_path: str, min_score: float = 0.7) -> datastructures.Page:
    """
    Acquires tables and figures from MI-inference of documents.
    """
    print("Acquiring tables and figures from MI-inference of documents...")
    # TODO: Make split more unique, so that files that naturally include "_page" do not fail
    page_data = datastructures.Page(int(os.path.basename(image_path).split("_page")[1].replace('.png', '')))
    image = cv2.imread(image_path)
    prediction = mi.infer_image_from_matrix(image)

    for pred in prediction:
        for idx, mask in enumerate(pred['masks']):
            label = mi.CATEGORIES2LABELS[pred["labels"][idx].item()]

            if pred['scores'][idx].item() < min_score:
                continue
            area = convert2coords(image, list(map(int, pred["boxes"][idx].tolist())))
            # score = pred["scores"][idx].item()

            if label == "table":
                table = datastructures.TableSegment(area)
                page_data.tables.append(table)
            elif label == "figure":
                figure = datastructures.ImageSegment(area)
                page_data.images.append(figure)
            else:
                continue
    print("Finished acquiring images and tables from MI-inference of documents.")
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
    Used to merge data from PDF-miner and MI-module together.
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


def remove_duplicates_from_list(list1: list, threshold=30):
    """
    Removes elements that reside in other elements.
    """
    for object1 in list1:
        for object2 in list1:
            if (object1 != object2):
                # Checks if object 2 is within object 1:
                if (object2.coordinates.x0 >= object1.coordinates.x0 - threshold and
                        object2.coordinates.x1 <= object1.coordinates.x1 + threshold and
                        object2.coordinates.y0 >= object1.coordinates.y0 - threshold and
                        object2.coordinates.y1 <= object1.coordinates.y1 + threshold):
                    list1.remove(object2)


def produce_data_from_coords(page, image_path, output_path, area_treshold=14400):
    """
    Checks if images and table coordinates are valid, 
    and saves them to the output folder in the "images" and "tables" folders.
    """
    path = None

    image_of_page = cv2.imread(image_path)
    
    for table_number in range(len(page.tables)):
        path = os.path.join(output_path, "tables", os.path.basename(image_path).replace(".png",
                            "_table" + str(table_number) + ".png"))
        save_content(image_of_page, path, page.tables[table_number], area_treshold)  
              
    for image_number in range(len(page.images)):
        path = os.path.join(output_path, "images", os.path.basename(image_path).replace(".png",
                            "_image" + str(image_number) + ".png"))
        save_content(image_of_page, path, page.images[image_number], area_treshold)

"""
Saves content of image or table as an image
"""
def save_content(image_of_page, path, obj, area_treshold):
    if (obj.coordinates.area() > area_treshold) and (
            obj.coordinates.is_negative() is False):
        try:
            extract_area.save_image_from_matrix(image_of_page, path, obj.coordinates)
        except Exception as x:
            print(x.__traceback__)
            print(x)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Segments pdf documents.")
    argparser.add_argument("-i", "--input", type=str, action="store", metavar="INPUT", help="Path to input folder.")
    argparser.add_argument("-o", "--output", type=str, action="store", metavar="OUTPUT", help="Path to output folder.")
    argparser.add_argument("-ii", "--invalid_input", type=str, action="store", metavar="INVALID_INPUT", default="invalid_inpt",
                           help="Path to invalid input folder.")
    argparser.add_argument("-a", "--accuracy", type=float, default=0.7, metavar="A",
                           help="Minimum threshold for the prediction accuracy. Value between 0 to 1.")
    argparser.add_argument("-m", "--machine", action="store_true",
                           help="Enable machine intelligence crossreferencing.")  # NOTE: Could be merged with accuracy arg
    argparser.add_argument("-t", "--temporary", action="store_true", default=False, help="Keep temporary files")
    argparser.add_argument("-c", "--clean", action="store_true", default=False,
                           help="Clear output folder before running.")
    argparser.add_argument("-s", "--schema", type=str, action="store", default="/schema/manuals_v1.3.schema.json",
                           help="Path to json schema.")
    argparser.add_argument("-d", "--download", action="store_true", default=False,
                           help="Downloads Grundfos data to input folder.")
    argv = argparser.parse_args()

    # Overwrite environment variables for this session, if program flags exists.
    if argv.input:
        os.environ["GRUNDFOS_INPUT_FOLDER"] = str(os.path.abspath(argv.input))
    if argv.invalid_input:
        os.environ["GRUNDFOS_INVALID_INPUT_FOLDER"] = str(os.path.abspath(argv.invalid_input))
    if argv.output:
        os.environ["GRUNDFOS_OUTPUT_FOLDER"] = str(os.path.abspath(argv.output))
    config_data.set_config_data_from_envs()
    config_data.check_config(["GRUNDFOS_INPUT_FOLDER",
                              "GRUNDFOS_OUTPUT_FOLDER"])

    for item in config:
        print(item, ": ", config[item])

    if argv.download is True:
        downloader.download_data(config["INPUT_FOLDER"])

    segment_documents(argv)
