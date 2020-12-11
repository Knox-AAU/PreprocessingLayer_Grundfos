from pdfminer.layout import LTTextLine, LTTextLineHorizontal, LTTextLineVertical, LTChar
import PDFminerLayoutExtractor
import PDFminerLineStreamer as PDFminerLineStreamer
import coordinates_calculator as CoordinatesCalculator
import ignore_coordinates
from datastructure.datastructure import Coordinates
import SegmentedPDF
import re
import sys

class TextAnalyser:
    __Pages__ = None
    __BlockTextFontSizes__ = None
    __NextLineIndex__ = None
    __PageIndex__ = None
    __LastLinesFontSize__ = -100000
    __CurrentText__ = None
    __CurrentTextStart__ = None
    __CurrentTextEnd__ = None
    __CurrentTextFontSize__ = None
    __FollowingLine__ = None
    
    def __init__(self, text_Line_List):
        self.CoordsCalc = CoordinatesCalculator.CoordinatesCalculator()
        self.LineStreamer = PDFminerLineStreamer.LineStreamer(text_Line_List)

    def segment_text(self):
        PDF = SegmentedPDF.SegPDF()
        SortedPages = []

        # Iterates though all pages, sorting all text into columns and ordering them
        for x in range(0, self.LineStreamer.NumOfPages):
            Page = self.LineStreamer.AllLinesFromPage(x)
            PageColumns = self.find_columns(Page)
            PageColumns = self.sort_columns(PageColumns)
            SortedPages.append(PageColumns)

        PDF.PDFtitle, PDF.PDFSubTitle = self.find_title(SortedPages[0])

        self.prepare_sectioning(SortedPages)

        self.find_sections(PDF)

        return PDF

    def prepare_sectioning(self, SortedPages):
        """does nessesary setup for section segmentation to begin"""
        self.__Pages__ = []
        for page in SortedPages:
            self.__Pages__.append([line for column in page for line in column])
        
        self.__NextLineIndex__ = 0
        self.__PageIndex__ = 0

        self.__BlockTextFontSizes__ = self.find_block_text_font_sizes(self.__Pages__[0])
        self.next_line()

    def find_sections(self, PDF):
        self.next_text()

        while self.__CurrentText__ != None:
            NewSection = SegmentedPDF.Section()

            if self.is_simular_size_in_list(self.__CurrentTextFontSize__, self.__BlockTextFontSizes__, 0.01):
                NewSection.Text = self.__CurrentText__
                NewSection.StartingPage = self.__CurrentTextStart__
                NewSection.EndingPage = self.__CurrentTextEnd__
                PDF.Sections.append(NewSection)
                self.next_text()
            else:
                NewSection.Title = self.__CurrentText__
                TitleFontSize = self.__CurrentTextFontSize__
                NewSection.StartingPage = self.__CurrentTextStart__
                self.next_text()
                self.find_subsections(NewSection, TitleFontSize)
                PDF.Sections.append(NewSection)

    def find_subsections(self, CurrentSection, TitleFontSize):
        while self.__CurrentText__ != None:
            if self.is_simular_size_in_list(self.__CurrentTextFontSize__, self.__BlockTextFontSizes__, 0.01):
                CurrentSection.Text += self.__CurrentText__
                self.next_text()
            elif self.is_simular_font_size(self.__CurrentTextFontSize__, TitleFontSize, 0.01) or TitleFontSize < self.__CurrentTextFontSize__:
                CurrentSection.EndingPage = self.__CurrentTextEnd__
                return
            else:
                NewSection = SegmentedPDF.Section()
                NewSection.Title = self.__CurrentText__
                NewSectionTitleFontSize = self.__CurrentTextFontSize__
                NewSection.StartingPage = self.__CurrentTextStart__
                self.next_text()
                self.find_subsections(NewSection, NewSectionTitleFontSize)
                CurrentSection.Sections.append(NewSection)
        
        CurrentSection.EndingPage = self.__CurrentTextEnd__

    def next_text(self):
        """Groups all sequential text of simular fontsize, saving results in self.__CurrentText__ and self.__CurrentTextFontSize__"""
        if self.__FollowingLine__ != None:
            self.__CurrentTextFontSize__ = self.font_size(self.__FollowingLine__)
            self.__CurrentText__ = self.__FollowingLine__.get_text()
            self.__CurrentTextStart__ = self.__PageIndex__ + 1

            self.next_line()

            while self.is_simular_font_size(self.__CurrentTextFontSize__, self.font_size(self.__FollowingLine__), 0.01):
                self.__CurrentText__ += self.__FollowingLine__.get_text()
                self.next_line()
        else:
            self.__CurrentText__ = None
            self.__CurrentTextFontSize__ = None

        if self.__PageIndex__ < len(self.__Pages__):
            self.__CurrentTextEnd__ = self.__PageIndex__ + 1
        else:
            self.__CurrentTextEnd__ = len(self.__Pages__)

    def next_line(self):
        """Find the next line and saves it in self.__FollowingLine__"""
        if self.__NextLineIndex__ < len(self.__Pages__[self.__PageIndex__]):
            self.__FollowingLine__ = self.__Pages__[self.__PageIndex__][self.__NextLineIndex__]
            self.__NextLineIndex__ += 1
            return
        else:
            self.__PageIndex__ += 1
            if self.__PageIndex__ < len(self.__Pages__):
                self.__BlockTextFontSizes__ = self.find_block_text_font_sizes(self.__Pages__[self.__PageIndex__])
                self.__NextLineIndex__ = 0
                self.next_line()
            else:
                self.__FollowingLine__ = None

    def find_title(self, FirstPage):
        try:

            LargestFontSize = 0

            #locates the line with largest fontsize on first page
            for ColumnIndex in range(0, len(FirstPage)):
                for LineIndex in range(0, len(FirstPage[ColumnIndex])):
                    LineFontSize = self.font_size(FirstPage[ColumnIndex][LineIndex])
                    if LineFontSize > LargestFontSize:
                        LargestFontSize = LineFontSize
                        LargestColumnIndex = ColumnIndex
                        LargestLineIndex = LineIndex

            PDFTitle = ""
            PDFSubTitle = ""
            
            # iterates over the column with the largest fontsize line
            # adding anything of simular size as pdftitle
            # adding subsequent lines as Subtitle
            for line in FirstPage[LargestColumnIndex]:
                if self.is_simular_font_size(self.font_size(line), LargestFontSize, 0.3):
                    PDFTitle += line.get_text()
                elif PDFTitle != "":
                    PDFSubTitle += line.get_text()

            del FirstPage[LargestColumnIndex]

            return PDFTitle, PDFSubTitle  
        except:
            return "", ""      

    def find_columns(self, Page):
        # Initializes first column
        AllColumns = []
        if len(Page) != 0:
            LastFontSize = self.font_size(Page[0])
            ColumnLines = [Page[0]]
            ColumnCoords = self.CoordsCalc.convert_object_to_coordinates(Page[0])

            # test all lines on page after the first
            for x in range(1, len(Page)):
                VertDist = self.CoordsCalc.compare_vertical_dist(Page[x], ColumnCoords)
                HoriDist = self.CoordsCalc.compare_horizontal_dist(Page[x], ColumnCoords)

                # test whether the new line is above the column coords
                # or if its larger then 2.5 line gab, compared to lastline
                # or if the column doesn't vertically overlap
                if VertDist > 0 or VertDist < LastFontSize * -2.5 or HoriDist != 0:
                    # new column
                    Column = [ColumnCoords, ColumnLines]
                    AllColumns.append(Column)
                    ColumnLines = [Page[x]]
                    ColumnCoords = self.CoordsCalc.convert_object_to_coordinates(Page[x])
                    LastFontSize = self.font_size(Page[x])
                else:
                    # Add to column
                    LastFontSize = self.font_size(Page[x])
                    ColumnLines.append(Page[x])
                    ColumnCoords.y0 = Page[x].y0
                    if Page[x].x0 < ColumnCoords.x0:
                        ColumnCoords.x0 = Page[x].x0
                    if Page[x].x1 > ColumnCoords.x1:
                        ColumnCoords.x1 = Page[x].x1


            # adds last column to columns
            if len(ColumnLines) != 0:
                Column = [ColumnCoords, ColumnLines]
                AllColumns.append(Column)

        if len(AllColumns) > 0:
            return AllColumns
        else:
            return []

    def sort_columns(self, Columns):
        SortedColumns = []

        while len(Columns) != 0:
            SelectedColumnCoords = Columns[0][0]
            SelectedColumnIndex = 0

            for x in range(1, len(Columns)):
                # test if the current column is more then five points further to the left then the selected
                if Columns[x][0].x0 / 5 - SelectedColumnCoords.x0 / 5 < -1:
                    SelectedColumnCoords = Columns[x][0]
                    SelectedColumnIndex = x
                # tests if the current column is futher up on the page then the selected
                elif self.CoordsCalc.compare_vertical_dist(Columns[x][0], SelectedColumnCoords) > 0:
                    SelectedColumnCoords = Columns[x][0]
                    SelectedColumnIndex = x

            SortedColumns.append(Columns[SelectedColumnIndex])
            del Columns[SelectedColumnIndex]

        return [Columns[1] for Columns in SortedColumns]

    def is_simular_size_in_list(self, FontSize, FontSizeList, EM):
        """Returns true if there is a fontsize in FontSizeList, of simularsize to FontSize given the error margine(%) EM"""
        for _FontSize in FontSizeList:
            if self.is_simular_font_size(FontSize, _FontSize, EM):
                return True

    def find_block_text_font_sizes(self, Page):
        NumOflines = 0
        FontList = [(0,0)]

        for line in Page:
            NumOflines += 1
            self.add_to_font_list(FontList, self.font_size(line))

        del FontList[0]
        LowerBound = NumOflines / 4

        #filters out the fontsizes which didn't appear more then the LowerBound, and only keeps the fontsize
        return [Font[0] for Font in FontList if Font[1] > LowerBound]

    def add_to_font_list(self, FontApperances, FontSize):
        for Apperance in FontApperances:
            if FontSize == Apperance[0]:
                Apperance[1] += 1
                return
        FontApperances.append([FontSize, 1])

    def is_simular_font_size(self, FontA, FontB, EM):
        #EM = Error Margine in procent (e.g. 0.1 = 10% error margine)
        return FontA / FontB < 1 + EM and FontA / FontB > 1 - EM

    def font_size(self, Textline):
        """returns Font size of textline"""
        if Textline == None:
            # isn't 0 to avoid needing to do additional checks, to avoid devide by zero errors in later calculations
            return 0.00000000001
        if isinstance(Textline, LTTextLineVertical):
            return round(Textline.x1 - Textline.x0, 4)
        return round(Textline.y1 - Textline.y0, 4)