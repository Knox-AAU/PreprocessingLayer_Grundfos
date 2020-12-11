import PyPDF4 as PDF
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

            # Load file 
            pdf_file = open(Path + '/' + file, 'rb')
            pdf_reader = PDF.PdfFileReader(pdf_file)

            for x in range(0, pdf_reader.numPages):
                #print('Processing file: %d    Page: %d' % (filenum,x))
                Text_file.write("\n################ PAGE: %d ###################\n" % x)
                Text_file.write(pdf_reader.getPage(x).extractText())

print("done")