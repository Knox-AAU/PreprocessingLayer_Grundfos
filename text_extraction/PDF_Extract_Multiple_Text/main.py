from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import os

Path = os.getcwd() + "/PDFs"
filenum = 1

for root, dirs, files in os.walk(Path):
    for file in files:
        if file.endswith(".pdf"):
            print('Prossing file: %d' % filenum)
            filenum += 1
            FileName = os.path.basename(file)

            Text_file = open("TEXTs/" + FileName.replace(".pdf", "_Text.txt"), "w")

            # Load your 
            filePointer = open(Path + '/' + file, 'rb')
            rsrcmgr = PDFResourceManager()
            laparams = LAParams(detect_vertical=True)
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            pdf = PDFPage.get_pages(filePointer)

            PageNum = 1

            for page in pdf:
                Text_file.write("\n################ PAGE: %d ###################\n" % PageNum)
                interpreter.process_page(page)
                layout = device.get_result()
                for lobj in layout:
                    if isinstance(lobj, LTTextBox):
                        Text_file.write(lobj.get_text())
                PageNum += 1

print("done")