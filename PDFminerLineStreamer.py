from pdfminer.layout import LTTextBox, LTTextLine
import coordinates_calculator

class LineStreamer():
    def __init__(self, text_Line_List):
        self.CoordsCalc = coordinates_calculator.CoordinatesCalculator()
        self.Pages = text_Line_List

        self.CurrentPage = self.Pages[0]
        self.CurrentPageNum = 0
        self.CurrentLine = -1
        self.NumOfPages = len(self.Pages)

        self.PageStreamers = {}
        
    def NextLine(self):
        """Goes though all pages, and returns the next line"""
        self.CurrentLine += 1
        if self.CurrentLine < len(self.CurrentPage):
            return self.CurrentPage[self.CurrentLine]
        else:
            self.CurrentPageNum += 1
            if self.CurrentPageNum < len(self.Pages):
                self.CurrentPage = self.Pages[self.CurrentPageNum]
                self.CurrentLine = -1
                return self.NextLine()
            else:
                self.CurrentLine = -1
                return None
    
    def Reset(self):
        """Resets line stream"""
        self.CurrentPage = self.Pages[0]
        self.CurrentPageNum = 0
        self.CurrentLine = 0

    def NextLineOfPage(self, PageNum):
        """Streams the lines of a specefic page"""
        if PageNum in self.PageStreamers:
            result = self.PageStreamers[PageNum].NextLine()
            if(result != None):
                return result
            else:
                del self.PageStreamers[PageNum]
                return None
        else:
            if PageNum < len(self.Pages):
                self.PageStreamers.update({PageNum : self.__PageStreamer__(self.Pages[PageNum])})
                return self.NextLineOfPage(PageNum)
            else:
                return None

    def ResetPage(self, PageNum):
        """Resets the stream of a specefic page"""
        if PageNum in self.PageStreamers:
            self.PageStreamers[PageNum].Reset()

    def AllLines(self):
        """Returns all lines of entire PDF, in one continues list"""
        Result = []

        for page in self.Pages:
            Result += page

        return Result

    def AllLinesFromPage(self, PageNum):
        """Returns all lines of a given page"""
        return self.Pages[PageNum]

    def LinesOnPage(self, PageNum):
        """returns the number of line of given page"""
        return len(self.Pages[PageNum])



    class __PageStreamer__():
        """private class used for returning lines of particular page"""
        def __init__(self, Page):
            self.Page = Page
            self.CurrentLine = -1

        def Reset(self):
            """resets the current page"""
            self.CurrentLine = -1

        def NextLine(self):
            """returns next line of page"""
            self.CurrentLine += 1
            if self.CurrentLine < len(self.Page):
                return self.Page[self.CurrentLine]
            else:
                return None