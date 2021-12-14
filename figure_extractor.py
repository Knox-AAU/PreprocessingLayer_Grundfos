import os
import subprocess
import json
from pandas import DataFrame


class FigureExtractor:
    """
    extract figures and captions using pdffigures2
    takes paths to output of pdffigures2 as input 
    """
    def __init__(self, inputPath, inputPathPDF, inputPathData, inputPathFig, outputPath):
        self.inputPath = inputPath
        self.inputPathPDF = inputPathPDF
        self.inputPathData = inputPathData
        self.inputPathFig = inputPathFig
        self.outputPath = outputPath

    def callPdfFigures2(self):
        """
        generate figures and captions 
        by calling command in terminal to run pdffigures2 
        with given inputPaths 
        """
        
        pdfPath = self.inputPathPDF + '/' #adding '/' because prefix is added to end of path (adding empty prefix)
        figPath = self.inputPathFig + '/'
        dataPath = self.inputPathData + '/'
        
        cmdArg = '"runMain org.allenai.pdffigures2.FigureExtractorBatchCli ' + pdfPath + ' -s stat_file.json -m ' + figPath + ' -d ' + dataPath +'"'
        try:
            result = subprocess.run(['sbt', cmdArg])
            return result
        except:
            print("Subprocess failed to run.")
            return
        
        
        
    """"

    def get_pdf_names(self):
        pdf_names = []

        for file in os.listdir(self.inputPathData):
            pdf_names.append(os.path.basename(file))

        return pdf_names
    def get_figures_and_captions(self):
        figures_and_captions = []

        for file in os.listdir(self.inputPath):
            figures_and_captions_one_manual = []
            with open(file) as extracted_json_figures:
                extracted_figures = json.load(extracted_json_figures)
                for figure in extracted_figures:
                    split_figure_path = os.path.basename(figure.renderURL).split("-")
                    figure_name = split_figure_path[2] + "-" + split_figure_path[3]
                    figures_and_captions_one_manual.append([figure_name, figure.caption])
            figures_and_captions.append(figures_and_captions_one_manual)

        return figures_and_captions
    
    
    def get_data_as_dataframe(self):
        pdf_names = self.get_pdf_names()
        figures_and_captions = self.get_figures_and_captions()

        dataframe = DataFrame(figures_and_captions, columns=pdf_names)

        return dataframe
    """

#temporary, in future run this through segment.py
if __name__ == '__main__':
    figureExtractor = FigureExtractor("pdffigures2/IO/OUTPUT_FIG")
    
    