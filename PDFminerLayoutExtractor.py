from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import os


class LayoutExtractor:
    """Class for extracting PDFminder.layout of a given PDF"""
    def __init__(self, PDFpath):
        self.rsrcmgr = PDFResourceManager()
        self.device = PDFPageAggregator(self.rsrcmgr, laparams=LAParams(detect_vertical=True))
        self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)
        self.PDFpath = PDFpath
        self.fp = open(os.path.join(os.getcwd(), PDFpath), 'rb')

    def __InitializePDF__(self):
        """Initializes PDF for other operations"""
        parser = PDFParser(self.fp)
        document = PDFDocument(parser)

        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        self.pages = PDFPage.create_pages(document)

    def ChangePDF(self, PDFpath):
        self.PDFpath = PDFpath
        self.fp = open(os.getcwd() + PDFpath, 'rb')
        
    def PageLayout(self, PageNum):
        """Extracts Layout of specefied page"""
        self.__InitializePDF__()

        for _PageNum, page in enumerate(self.pages):
            if(_PageNum == PageNum):
                self.interpreter.process_page(page)
                return self.device.get_result()

    def AllLayouts(self):
        """Extracts the layout of all pages"""
        self.__InitializePDF__()

        Layouts = []
        for page in self.pages:
            self.interpreter.process_page(page)
            Layouts.append(self.device.get_result())

        return Layouts

    def GetWidthAndHeightOfPage(self, PageNum):
        """returns the width and height of a specefied page in points mesurements"""
        self.__InitializePDF__()

        for _PageNum, page in enumerate(self.pages):
            if(_PageNum == PageNum):
                return page.mediabox[2], page.mediabox[3]
