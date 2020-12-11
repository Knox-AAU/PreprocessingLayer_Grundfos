"""
This module provides datastructures for pages and page-elements
"""

class Coordinates:
    """
    Describes an area defined by two sets of coordinates.
    """
    def __init__(self, x0: float, y0 : float, x1: float, y1: float):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def to_string(self) -> str:
        """
        Return the coordinates in string format.
        """
        return "({0}, {1})({2}, {3})".format(self.x0, self.y0, self.x1, self.y1)

    def area(self) -> float:
        """
        Calculates and returns the size of the area spanning the coordinates.
        """
        return abs(self.x0 - self.x1) * abs(self.y0 - self.y1)
    
    def is_negative(self):
        if (self.x0 < 0) or (self.x1 < 0) or (self.y0 < 0) or (self.y1 < 0):
            return True
        else:
            return False

class Text_Line_Coordinates(Coordinates):
    def __init__(self, x0: float, y0 : float, x1: float, y1: float, element):
        super().__init__(x0, y0, x1, y1)
        self.text_Line_Element = element

class TextSegment:
    """
    Describes a textsegment found on a page.
    """
    def __init__(self, coordinates, header, value):
        self.coordinates = coordinates
        self.header = header
        self.value = value


class ImageSegment:
    """
    Describes an imagesegment found on a page.
    """
    path = None
    coordinates: Coordinates = None
    page_number: int
    def __init__(self, coordinates):
        self.coordinates = coordinates


class TableSegment:
    """
    Describes a tablesegment found on a page.
    """
    path = None
    coordinates: Coordinates = None
    page_number: int
    def __init__(self, coordinates: Coordinates):
        self.coordinates = coordinates

class Page:
    """
    Contains the content of a page.
    """
    def __init__(self, page_number: int):
        self.page_number = page_number
        self.text_sections = []
        self.images = []
        self.tables = []

    def add_from_page(self, page):
        """
        Adds the content of a page to this page.
        """
        self.text_sections.extend(page.text_sections)
        self.images.extend(page.images)
        self.tables.extend(page.tables)
    
    def add_from_lists(self, text_sections, images, tables):
        """
        Adds the content of a page to this page.
        """
        self.text_sections.extend(text_sections)
        self.images.extend(images)
        self.tables.extend(tables)