import os
import subprocess
import json
import logging
import traceback
from labelGenerator import *

class IDGenerator:
    def __init__(self, seed = 0):
        self.ID = seed
    def generateID(self):
        ID = self.ID
        self.ID += 1
        return ID
        

class FigureExtractor:
    """
    extract figures and captions using pdffigures2
    input: path/to/pdf_folder, path/to/figure_folder, path/to/json_folder, path/to/store_output
    """
    def __init__(self, inputPathPDF, inputPathFig, inputPathData, outputPath, sourcePath = '../pdf-Figures2'):
        self.inputPathPDF = inputPathPDF
        self.inputPathData = inputPathData
        self.inputPathFig = inputPathFig
        self.outputPath = outputPath #where to store pruned JSON files
        self.sourcePath = sourcePath #directory of pdffigures2 
        


    def callPdfFigures2(self):
        """
        generate figures and captions 
        by calling command in cmd to run pdffigures2 with given input paths 
        """
        pdfPath = self.inputPathPDF + '/' #adding '/' because prefix is added to end of path (adding empty prefix)
        figPath = self.inputPathFig + '/'
        dataPath = self.inputPathData + '/'
        
        cmdArg = "runMain org.allenai.pdffigures2.FigureExtractorBatchCli " + pdfPath + ' -s stat_file.json -m ' + figPath + ' -d ' + dataPath
        cwdPath = self.sourcePath
        
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
        
        ID = IDGenerator(0)
        
        for file in os.listdir(figureDataPath):
            pdfID = self.get_filename(file)
            print(pdfID)	
            
            with open(os.path.join(figureDataPath, file), encoding="utf8") as figureData:
                prunedJson = json.load(figureData, encoding="utf8")
            
            '''
            remove unnecessary fields, add pdf id and figure id
            '''
            for figure in prunedJson:
                figure.pop('captionBoundary', None)
                figure.pop('figType', None)
                figure.pop('page', None)
                figure.pop('regionBoundary', None)
                figure.pop('renderDpi', None)
                figure.update({"pdfID": pdfID})
                figure.update({"figID": ID.generateID()})
        
            '''
            if the resulting pruned json is not empty, create a new json file in output path
            '''
            if(len(prunedJson) != 0):
                filePath = os.path.join(os.path.dirname(os.getcwd()), self.outputPath)
                newfile = open(os.path.join(filePath, pdfID + ".json"), "w", encoding='utf-8')
                json.dump(prunedJson, newfile, sort_keys = True, indent = 2)
                
    def labelFigures(self, max_labels):
        labelGen = labelGenerator()
        figureDataPath = os.path.join(os.path.dirname(os.getcwd()), self.outputPath)
        for file in os.listdir(figureDataPath):
            pdfID = self.get_filename(file)
            print(pdfID)	
            
            with open(os.path.join(figureDataPath, file), encoding="utf8") as figureData:
                pdfJSON = json.load(figureData, encoding="utf8")
                for fig in pdfJSON:
                    label = labelGen.get_label(fig["figID"], max_labels)
                    fig.update({"label": label})
                    
            filePath =os.path.join(os.path.dirname(os.getcwd()), figureDataPath)
            newfile = open(os.path.join(filePath, pdfID + ".json"), "w", encoding='utf-8')
            json.dump(pdfJSON, newfile, indent = 2)
                    
                    
#temporary, in future run this through segment.py
if __name__ == '__main__':
    figureExtractor = FigureExtractor('IO/INPUT_ALL', 'IO/OUTPUT_FIG', 'IO/OUTPUT_DATA', 'OUTPUT_PRUNED')
    figureExtractor.callPdfFigures2()
    figureExtractor.get_figure_data()
    figureExtractor.labelFigures(3)