import os
import subprocess
import json
import logging
import traceback

class FigureExtractor:
    """
    extract figures and captions using pdffigures2
    input: path/to/pdf_folder, path/to/figure_folder, path/to/json_folder, path/to/store_output
    """
    def __init__(self, sourcePath, inputPathPDF, inputPathFig, inputPathData, outputPath, cwdPath = '/Users/Bruger/Desktop/AAU software Bachelor/5. sem/KNOX/pdfFigures2'): #TODO change default cwdPath to match server
        self.sourcePath = sourcePath
        self.inputPathPDF = inputPathPDF
        self.inputPathData = inputPathData
        self.inputPathFig = inputPathFig
        self.outputPath = outputPath #where to store pruned JSON files
        self.cwdPath = cwdPath #directory of pdffigures2 
        


    def callPdfFigures2(self):
        """
        generate figures and captions 
        by calling command in cmd to run pdffigures2 with given input paths 
        """
        pdfPath = self.inputPathPDF + '/' #adding '/' because prefix is added to end of path (adding empty prefix)
        figPath = self.inputPathFig + '/'
        dataPath = self.inputPathData + '/'
        
        cmdArg = "runMain org.allenai.pdffigures2.FigureExtractorBatchCli " + pdfPath + ' -s stat_file.json -m ' + figPath + ' -d ' + dataPath
        cwdPath = self.cwdPath
        
        try:
            result = subprocess.run(['sbt', cmdArg], shell=True, cwd = cwdPath)
            return result
        except Exception as e:
            print("Subprocess failed to run.")
            logging.error(traceback.format_exc())
            return
        
    def get_filename(self, file):
        filename, file_extension = os.path.splitext(file)
        return filename

    def get_figure_data(self):

        '''
        open each json file in input dicretory
        '''
        figureDataPath = os.path.join(self.sourcePath, self.inputPathData)
        
        for file in os.listdir(figureDataPath):
            pdfID = self.get_filename(file)
            print(pdfID)	
            
            with open(os.path.join(figureDataPath, file), encoding="utf8") as figureData:
                prunedJson = json.load(figureData, encoding="utf8")

            '''
            remove unnecessary fields
            '''
            for figure in prunedJson:
                figure.pop('captionBoundary', None)
                figure.pop('figType', None)
                figure.pop('page', None)
                figure.pop('regionBoundary', None)
                figure.pop('renderDpi', None)
                figure.update({"pdfID": pdfID})
        
            '''
            if the resulting pruned json is not empty, create a new json file in output path
            '''
            if(len(prunedJson) != 0):
                filePath =os.path.join(os.path.dirname(os.getcwd()), self.outputPath)
                newfile = open(os.path.join(filePath, pdfID + ".json"), "w", encoding='utf-8')
                json.dump(prunedJson, newfile, sort_keys = True, indent = 2)
                
#temporary, in future run this through segment.py
if __name__ == '__main__':
    figureExtractor = FigureExtractor('/Users/Bruger/Desktop/AAU software Bachelor/5. sem/KNOX/pdfFigures2', 'IO/INPUT', 'IO/OUTPUT_FIG', 'IO/OUTPUT_DATA', 'OUTPUT_PRUNED')
    figureExtractor.callPdfFigures2()
    figureExtractor.get_figure_data()