import os
import subprocess
import json
from pandas import DataFrame

class FigureExtractor:

    def __init__(self, inputPath):
        self.inputPath = inputPath

    def extract_figures_and_captions(self):
        try:
            result = subprocess.run(['sbt', '"runMain org.allenai.pdffigures2.FigureExtractorBatchCli'
                                            ' /path/to/pdf_directory/ -s stat_file.json -m /figure/image/output/prefix'
                                            ' -d /figure/data/output/prefix"'])
            return result
        except:
            print("Subprocess failed to run.")
            return

    def get_data_as_dataframe(self):
        manual_names = self.get_manual_names()
        figures_and_captions = self.get_figures_and_captions()

        dataframe = DataFrame(figures_and_captions, columns=manual_names)

        return dataframe

    def get_manual_names(self):
        manual_names = []

        for file in os.listdir(self.inputPath):
            manual_names.append(os.path.basename(file))

        return manual_names

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