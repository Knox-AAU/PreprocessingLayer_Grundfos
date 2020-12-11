import os
import pdftotext
from termcolor import colored

Path = os.getcwd() + "/PDFs"
filenum = 1

for root, dirs, files in os.walk(Path):
    for file in files:
        if file.endswith(".pdf"):
            print('Processing file: %d' % filenum)
            filenum += 1
            
            FileName = os.path.basename(file)

            Text_file = open("TEXTs/" + FileName.replace(".pdf", "_Layout.txt"), "w")

            # Load your PDF
            with open("PDFs/" + FileName, "rb") as f:
                pdf = pdftotext.PDF(f, raw=False)

            PageNum = 1

            for page in pdf:
                Text_file.write("\n################ PAGE: %d ###################\n" % PageNum)
                Text_file.write(page)
                PageNum += 1

print("done")