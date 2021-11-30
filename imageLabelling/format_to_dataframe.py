import os
import json
from pandas import DataFrame

class DataFrameFormatter:
    def __init__(self, inputPath):
        self.inputPath = inputPath

    def get_data_as_dataframe(self):
        pdf_names = self.get_pdf_names()
        figures_and_captions = self.get_figures_and_captions()

        dataframe = DataFrame(figures_and_captions, columns=pdf_names)

        return dataframe

    def get_pdf_names(self):
        pdf_names = []

        for file in os.listdir(self.inputPath):
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