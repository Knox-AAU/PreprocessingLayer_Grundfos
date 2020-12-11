from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import io
import os

def main():
    count = 0
    for filename in os.listdir('lit'):
        try:
            path = 'lit/' + filename
            text = get_text(path)
            text = text.encode('utf-16')
            newpath = 'demo/' + removefiletype(filename) + '.txt'
            f = open(newpath, 'w')
            f.write(str(text))
            f.close()
            count += 1
            print(filename + count)
        except:
            print(filename + " is a peice of shit")

def get_text(path):
    fp = open(path, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(detect_vertical=True)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp)
    result = []
    PageNum = 1

    for page in pages:
        interpreter.process_page(page)
        layout = device.get_result()
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
                result.append(text)
        PageNum += 1
    return result

def removefiletype(string):
    temp = string.split('.')
    return temp[0]


def extractLines():
    result = []
    for filename in os.listdir('lit'):
        try:
            path = 'lit/' + filename
            result = get_text(path)
            print(filename + " has been succesfully processed!")
        except:
            print(filename + " file could not be processed :(")
    return result

if __name__ == "__main__":
    main()
