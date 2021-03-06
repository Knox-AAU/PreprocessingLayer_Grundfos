"""
This module has the functionality of initialising PDFMiner and finding all images and figures
"""

import os
import sys
import cv2
import argparse
import numpy as ny
import time
import shutil
import segment
import IO_handler
import datastructure.datastructure as datastructure
import utils.pdf2png as pdf2png
import concurrent.futures as cf
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import (
    LAParams,
    LTTextBox,
    LTTextLine,
    LTText,
    LTChar,
    LTFigure,
    LTImage,
    LTRect,
    LTCurve,
    LTLine,
)
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
import config_data
from config_data import config

FIGURES = os.path.join("tmp", "figures")
IMAGES = os.path.join("tmp", "images")
ANNOTATED = os.path.join("tmp", "images_annotated")
LINES = os.path.join("tmp", "line_cords")

start_time = time.time()


# This function is necessary if arguments are used instead of environment variables
# because environment variables created from os.environ can't be seen across Processes
def initz_paths(args):
    if args.input:
        os.environ["GRUNDFOS_INPUT_FOLDER"] = str(os.path.abspath(args.input))
    if args.output:
        os.environ["GRUNDFOS_OUTPUT_FOLDER"] = str(os.path.abspath(args.output))
    config_data.check_config(["GRUNDFOS_INPUT_FOLDER", "GRUNDFOS_OUTPUT_FOLDER"])


class PDF_file:
    """
    Contains information regarding each PDF file.
    """

    def __init__(self, file, args):
        try:
            self.file_name = os.path.basename(file)
            temp_pages, self.interpreter, self.device = init_file(args, self.file_name)
            self.pages = []
            page_num = 0
            for page in temp_pages:
                page_num += 1
                self.pages.append(PDF_page(self, args, page))
        except MemoryError:
            print(
                "PDF miner ran out of moemory, and pdf file was force skiped at page: "
                + page_num
            )
            return


class PDF_page:
    """
    Contains information regarding each PDF page and all the lists of objects found by PDFMiner.
    """

    def __init__(self, owner, args, page):
        self.LTImageList = []
        self.LTRectList = []
        self.LTRectLineList = []
        self.LTCurveList = []
        self.LTLineList = []
        self.LTTextLineList = []
        self.TableLines = []
        self.TableCoordinates = []
        owner.interpreter.process_page(page)
        self.layout = owner.device.get_result()

        self.PDFfile_width = page.mediabox[2]  # - 35
        self.PDFfile_height = page.mediabox[3]  # - 31

        # Prerequisites for image processing
        self.image_name = (
            owner.file_name.replace(".pdf", "_page")
            + str(len(owner.pages) + 1)
            + ".png"
        )
        self.image_number = len(owner.pages) + 1
        self.first_image = cv2.imread(
            os.path.join(os.path.join(config["OUTPUT_FOLDER"], IMAGES), self.image_name)
        )
        self.height, self.width = self.first_image.shape[:2]

        self.actualHeightModifier = self.height / self.PDFfile_height
        self.actualWidthModifier = self.width / self.PDFfile_width


def init_file(args, fileName):
    """
    This function initialises PDFMiner
    """
    fp = open(os.path.join(config["INPUT_FOLDER"], fileName), "rb")
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(detect_vertical=False)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    return PDFPage.get_pages(fp), PDFPageInterpreter(rsrcmgr, device), device


def search_page(page, args):
    """
    Gets all PDFMiner objects from a page.
    """
    index = 1
    figureIndex = 1
    # find all images and figures first.
    for lobj in page.layout:
        if isinstance(lobj, LTImage):
            index = index + 1
            figureIndex = figureIndex + 1

            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            if (
                x0 < page.PDFfile_width
                and x0 > 0
                and x1 < page.PDFfile_width
                and x1 > 0
            ) and (
                y0 < page.PDFfile_height
                and y0 > 0
                and y1 < page.PDFfile_height
                and y1 > 0
            ):
                newLTImage = datastructure.Coordinates(x0, y0, x1, y1)
                page.LTImageList.append(newLTImage)
                save_figure(lobj, page, figureIndex, args)

        if isinstance(lobj, LTRect):
            index = index + 1
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            if (
                x0 < page.PDFfile_width
                and x0 > 0
                and x1 < page.PDFfile_width
                and x1 > 0
            ) and (
                y0 < page.PDFfile_height
                and y0 > 0
                and y1 < page.PDFfile_height
                and y1 > 0
            ):
                result = check_if_line(
                    x0, y0, x1, y1
                )  # check if the rectangle is a line instead of a rectangle.
                if result != 0:  # it is a line
                    if result == 1:  # horizontal line
                        newLTLine = datastructure.Coordinates(x0, y0, x1, y0)
                        page.LTRectLineList.append(newLTLine)
                    elif result == 2:  # vertical line
                        newLTLine = datastructure.Coordinates(x0, y0, x0, y1)
                        page.LTRectLineList.append(newLTLine)
                else:
                    newLTRect = datastructure.Coordinates(x0, y0, x1, y1)
                    page.LTRectList.append(newLTRect)

        if isinstance(lobj, LTFigure):
            for inner_obj in lobj:
                if isinstance(inner_obj, LTImage):
                    index = index + 1
                    figureIndex = figureIndex + 1

                    x0, y0, x1, y1 = (
                        inner_obj.bbox[0],
                        inner_obj.bbox[1],
                        inner_obj.bbox[2],
                        inner_obj.bbox[3],
                    )
                    if (
                        x0 < page.PDFfile_width
                        and x0 > 0
                        and x1 < page.PDFfile_width
                        and x1 > 0
                    ) and (
                        y0 < page.PDFfile_height
                        and y0 > 0
                        and y1 < page.PDFfile_height
                        and y1 > 0
                    ):
                        newLTImage = datastructure.Coordinates(x0, y0, x1, y1)
                        page.LTImageList.append(newLTImage)
                        save_figure(inner_obj, page, figureIndex, args)

                # find all lines and curves.
                elif isinstance(inner_obj, LTCurve):
                    index = index + 1
                    x0, y0, x1, y1 = (
                        inner_obj.bbox[0],
                        inner_obj.bbox[1],
                        inner_obj.bbox[2],
                        inner_obj.bbox[3],
                    )
                    newLTCurve = datastructure.Coordinates(x0, y0, x1, y1)
                    page.LTCurveList.append(newLTCurve)

        if isinstance(lobj, LTLine):
            index = index + 1
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            newLTLine = datastructure.Coordinates(x0, y0, x1, y1)
            page.LTLineList.append(newLTLine)

        # find all text.
        if isinstance(lobj, LTTextBox):
            for obj in lobj:
                if isinstance(obj, LTTextLine):
                    index = index + 1
                    x0, y0, x1, y1 = obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3]
                    newLTTextBox = datastructure.Text_Line_Coordinates(
                        x0, y0, x1, y1, obj
                    )
                    page.LTTextLineList.append(newLTTextBox)


def make_page(page: PDF_page):
    """
    Converts a PDF_page object into Page object.
    """
    result = datastructure.Page(page.image_number)
    image_and_rectangle_list = page.LTImageList
    image_and_rectangle_list.extend(page.LTRectList)
    result.add_from_lists(
        [],
        convert_to_datastructure(
            convert_to_pixel_height(page, image_and_rectangle_list),
            datastructure.ImageSegment,
        ),
        convert_to_datastructure(
            convert_to_pixel_height(page, page.TableCoordinates),
            datastructure.TableSegment,
        ),
    )
    return result


def convert_to_pixel_height(page: PDF_page, object_list: list):
    """
    Converts all PDFMiner objects measured in points into their respective pixel coordinates. (Note that the y0 and y1 are swapped to match the Page data type.)
    """
    result_elements = []
    if object_list is not None:
        for element in object_list:
            result_elements.append(
                datastructure.Coordinates(
                    page.actualWidthModifier * element.x0,
                    page.actualHeightModifier * element.y1,
                    page.actualWidthModifier * element.x1,
                    page.actualHeightModifier * element.y0,
                )
            )
    return result_elements


def convert_to_datastructure(object_list: list, desired_object: object):
    """
    Converts a list of objects into the desired object type.
    """
    result_obj_list = []
    for obj in object_list:
        result_obj_list.append(desired_object(obj))

    return result_obj_list


def check_if_line(x0, y0, x1, y1, threshold=5):
    """
    Checks if a object actually is a line based on the objects coordinates.
    """
    x = abs(x1 - x0)
    y = abs(y1 - y0)

    if y < threshold:  # horizontal line
        return 1

    if x < threshold:  # vertical line
        return 2

    return 0


def save_figure(lobj, page, figureIndex, args):
    """
    Saves embedded image files from the PDF.
    """
    file_stream = lobj.stream.get_rawdata()
    file_extension = IO_handler.get_file_extension(file_stream[0:4])

    if file_extension != None:
        figureName = (
            page.image_name.replace(".png", "") + str(figureIndex) + file_extension
        )

        file_obj = open(
            os.path.join(os.path.join(config["OUTPUT_FOLDER"], FIGURES), figureName),
            "wb",
        )
        file_obj.write(lobj.stream.get_rawdata())
        file_obj.close()


def flip_y_coordinates(page):
    """
    Flips the y coordinates for all lists, to match the pixel coordinate behavior. (This is done because the y coordinates measured in the points unit grow from the bottom to the top.)
    """
    flip_y_coordinate(page, page.LTImageList)
    flip_y_coordinate(page, page.LTRectList)
    flip_y_coordinate(page, page.LTRectLineList)
    flip_y_coordinate(page, page.LTCurveList)
    flip_y_coordinate(page, page.LTLineList)
    flip_y_coordinate(page, page.LTTextLineList)


def flip_y_coordinate(page, object_List):
    """
    Flips y coordinates by substracting it with the total height of a page.
    """
    for element in object_List:
        element.y0 = page.PDFfile_height - element.y0
        element.y1 = page.PDFfile_height - element.y1


def paint_pngs(page, args):
    """
    Paints a page with all of the objects found by PDFMiner in each their color and outputs a PNG file.
    """

    thickness = -1
    lineThickness = 40
    image = cv2.rectangle(page.first_image, (0, 0), (0, 0), (255, 255, 255), 1)

    # LTRect:
    colorPink = (127, 255, 0)
    image = paint(image, page, page.LTRectList, colorPink, thickness)

    # LTImage:
    colorGreen = (0, 255, 0)  # green - image
    image = paint(image, page, page.LTImageList, colorGreen, thickness)

    # LTCurve:
    colorBlue = (255, 0, 0)  # blue - figure
    image = paint(image, page, page.LTCurveList, colorBlue, lineThickness)

    # LTLines:
    image = paint(image, page, page.LTLineList, colorBlue, lineThickness)
    # LTRectlines:
    color_Light_Blue = (255, 191, 0)
    image = paint(image, page, page.LTRectLineList, color_Light_Blue, lineThickness)

    # tables:
    colorRed = (0, 0, 255)
    image = paint(image, page, page.TableCoordinates, colorRed, thickness)

    # LTTextlines:
    colorBlack = (0, 0, 0)  # black - text
    # colorWhite = (255, 255, 255) #white
    image = paint(image, page, page.LTTextLineList, colorBlack, thickness)
    print(page.image_name)

    cv2.imwrite(
        os.path.join(config["OUTPUT_FOLDER"], ANNOTATED, page.image_name), image
    )  # save picture


def paint(image, page, objectList, color, thickness):
    """
    Converts the coordinates into pixels before drawing the mask on the PNG file using OpenCV.
    """
    for element in objectList:
        start_point = (
            round(element.x0 * page.actualWidthModifier),
            round(element.y0 * page.actualHeightModifier),
        )
        end_point = (
            round(element.x1 * page.actualWidthModifier),
            round(element.y1 * page.actualHeightModifier),
        )

        image = cv2.rectangle(image, start_point, end_point, color, thickness)

    return image


def look_through_LTRectLine_list(page, args):
    # This function has a very large time complexity.
    """
    Finds bounding box coordinates, by grouping horizontal and vertical lines.
    """
    Table_Dictionary = {}
    table_Index_key = 0
    line_list = page.LTRectLineList.copy()

    something_was_changed = False

    while True:
        if something_was_changed == True:
            something_was_changed = False
            for LT_Line_element in line_list:
                result = on_segment(LT_Line_element, Table_Dictionary)
                if result[0] == True:
                    key = result[1]
                    if key in Table_Dictionary:
                        Table_Dictionary[key].append(LT_Line_element)
                        line_list.remove(LT_Line_element)
                        something_was_changed = True
        else:
            if len(line_list) > 0:
                Table_Dictionary[table_Index_key] = [line_list[0]]
                line_list.remove(line_list[0])
                table_Index_key = table_Index_key + 1
                something_was_changed = True
            else:
                break

    # Delete single elements in the dictionary:
    Table_Dictionary = remove_single_elements(Table_Dictionary)

    # find retangle coordinates for each grouping of table lines:
    for dicelement in Table_Dictionary.values():
        coords = return_retangle_coordinates_for_table(dicelement)
        if coords.x0 != 0 and coords.y0 != 0 and coords.x1 != 0 and coords.y1 != 0:
            page.TableCoordinates.append(coords)


def on_segment(Line_element, dictionary):
    """
    This function determines if a line intersects another line at one point.
    """
    offset = 1
    for key, value in dictionary.items():
        if len(value) > 0:
            for element in value:
                if (
                    round(Line_element.x0) - offset
                    <= max(round(element.x0), round(element.x1))
                    and round(Line_element.x0) + offset
                    >= min(round(element.x0), round(element.x1))
                    and round(Line_element.y0) - offset
                    <= max(round(element.y0), round(element.y1))
                    and round(Line_element.y0) + offset
                    >= min(round(element.y0), round(element.y1))
                ):
                    return True, key
                elif (
                    round(Line_element.x1) - offset
                    <= max(round(element.x0), round(element.x1))
                    and round(Line_element.x1) + offset
                    >= min(round(element.x0), round(element.x1))
                    and round(Line_element.y1) - offset
                    <= max(round(element.y0), round(element.y1))
                    and round(Line_element.y1) + offset
                    >= min(round(element.y0), round(element.y1))
                ):
                    return True, key
    return False, ""


def remove_single_elements(dictionary):
    """
    This function pops entries of a dictionary where the value list only has one element in it.
    """
    dictionary_Copy = dictionary.copy()
    for key, value in dictionary_Copy.items():
        if len(value) == 1:
            dictionary_Copy[key].pop()
    return dictionary_Copy


def return_retangle_coordinates_for_table(dicelement):
    """
    This function returns the bounding box of a grouping of lines
    """
    lower_left_x0 = 0
    lower_left_y0 = 0
    upper_right_x1 = 0
    upper_right_y1 = 0

    index = 0
    for element in dicelement:
        if index > 0:
            if round(element.x0) <= round(lower_left_x0) and round(element.y0) >= round(
                lower_left_y0
            ):
                lower_left_x0 = round(element.x0)
                lower_left_y0 = round(element.y0)
            elif round(element.x1) >= round(upper_right_x1) and round(
                element.y1
            ) <= round(upper_right_y1):
                upper_right_x1 = round(element.x1)
                upper_right_y1 = round(element.y1)
        else:
            lower_left_x0 = round(element.x0)
            lower_left_y0 = round(element.y0)
            upper_right_x1 = round(element.x1)
            upper_right_y1 = round(element.y1)
        index = index + 1

    table_coordinate = datastructure.Coordinates(
        lower_left_x0, lower_left_y0, upper_right_x1, upper_right_y1
    )
    return table_coordinate


def remove_text_within(page, object_List):
    """
    This function removes all text elements inside the objects in the list it is called with.
    """
    text_Line_List = page.LTTextLineList.copy()
    for text_Element in text_Line_List:
        element_Found = False
        for object_Element in object_List:
            # If the whole text line is within the object, delete it:
            if (
                text_Element.x0 >= object_Element.x0
                and text_Element.y1 <= object_Element.y1
            ) and (
                text_Element.x1 <= object_Element.x1
                and text_Element.y0 >= object_Element.y0
            ):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break
            # If the text line starts within the object (per x-coordinates), also delete it:
            elif (
                text_Element.x0 <= object_Element.x1
                and text_Element.x0 >= object_Element.x0
            ) and (
                text_Element.y1 <= object_Element.y1
                and text_Element.y0 >= object_Element.y0
            ):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break
            # If the text line ends within the object (per x-coordinates), also delete it:
            elif (
                text_Element.x1 >= object_Element.x0
                and text_Element.x1 <= object_Element.x1
            ) and (
                text_Element.y1 <= object_Element.y1
                and text_Element.y0 >= object_Element.y0
            ):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break
                # If the text lines bottom is partly within the object (per y-coordinates), also delete it:
            elif (
                text_Element.y1 >= object_Element.y0
                and text_Element.y1 <= object_Element.y1
            ) and (
                text_Element.x1 <= object_Element.x1
                and text_Element.x0 >= object_Element.x0
            ):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break
            # If the text lines top is partly within the object (per y-coordinates), also delete it:
            elif (
                text_Element.y0 <= object_Element.y1
                and text_Element.y0 >= object_Element.y0
            ) and (
                text_Element.x1 <= object_Element.x1
                and text_Element.x0 >= object_Element.x0
            ):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break
            # Should there be a check which also deletes it if it starts before and ends after the object (goes through)? #TODO
        if element_Found == True:
            continue
