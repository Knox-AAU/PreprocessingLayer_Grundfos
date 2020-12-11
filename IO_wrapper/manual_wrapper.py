"""
Module responsible for making the output of the segmentation. 
More specifically it is preparing data for the actural wrapper used (https://git.its.aau.dk/Knox/source-data-io)
"""

from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
import datastructure.datastructure as ds
import os
import datetime
import SegmentedPDF

class Schema_Manual(Model):
    """
    Data structure for manuals.
    """
    def __init__(self, pdf_title, publisher, published_at, pdf_sections, pdf_tables, pdf_images):
        self.title = pdf_title
        self.publisher = publisher
        self.published_at = published_at #Can we get this information??
        self.sections = pdf_sections
        self.table_list = pdf_tables
        self.image_list = pdf_images
        
class Schema_Section():
    """
    Data structure for sections in the manuals.
    """
    def __init__(self, section_header, section_pages, section_paragraphs, subsections):
        self.header = section_header
        self.pages = section_pages
        self.paragraphs = section_paragraphs
        self.subsections = subsections

class Schema_Paragraph():
    """
    Data structure for text paragraphs in the manuals.
    """    
    def __init__(self, file_text):
        self.text = file_text

class Schema_Image():
    """
    Data structure for figures in manuals.
    """
    def __init__(self, page_span, image_value):
        self.page_number = page_span
        self.value = image_value

class Schema_Table():
    """
    Data structure for the tables in manuals.
    """
    def __init__(self, page_span, table_value):
        self.page_number = page_span
        self.value = table_value


def create_output(segmented_pdf: SegmentedPDF.SegPDF, pages: ds.Page, file_name, schema_path, output_path):
    """
    Creates the output to JSON using knox-source-data-io module: https://git.its.aau.dk/Knox/source-data-io
    """
    #Create list of text-sections
    pdf_sections = create_sections(segmented_pdf.Sections)
    
    #Create list of tables and images
    pdf_illustrations = create_illustrations(pages)
    pdf_tables = pdf_illustrations[0]
    pdf_images = pdf_illustrations[1]

    #Create object for JSON
    export_able_object = Schema_Manual(segmented_pdf.PDFtitle, "Grundfos A/S", "", pdf_sections, pdf_tables, pdf_images)

    # Generate
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", generated_at= str(datetime.datetime.now()), version="1.1.0"), schema_path)
    output_name = str(file_name.replace(".pdf", "") + "_output.json")
    filename = os.path.join(output_path, output_name)
    
    # Serialize object to json
    with open(filename, 'w', encoding='utf-16') as outfile:
        handler.write_json(export_able_object, outfile)

def create_sections(text_sections):
    """
    Creates the datastructure for text-sections.
    """
    sections = []
    for section in text_sections:
        visited_section = visit_subsections(section)
        if visited_section is not None: # Do not add the section if it is "null/none"
            sections.append(visited_section)
    return sections

def visit_subsections(root: SegmentedPDF.Section):
    """
    Recursive visitor for the sections and their subsections.
    """
    if root.Sections is not None:
        schema_section = []
        for section in root.Sections:
            paragraph = Schema_Paragraph(section.Text)
            if (section.StartingPage == section.EndingPage):
                page = str(section.StartingPage)
            else:
                page = str(str(section.StartingPage) + "-" + str(section.EndingPage))
            schema_section.append(Schema_Section(section.Title, page, paragraph, visit_subsections(section)))
        if len(schema_section) == 0: #Remove empty lists
            return None
        else:
            return schema_section
    return None

def create_illustrations(pages):
    """
    Returns a tuple of lists of the tables and images found on ALL pages in the pdf-file.
    """
    pdf_tables = []
    pdf_images = []
    for page in pages:
        #Create table-list
        for table in page.tables:
            pdf_tables.append(Schema_Table(page.page_number, table.path))
        #Create image-list
        for image in page.images:
            pdf_images.append(Schema_Image(page.page_number, image.path))
    return (pdf_tables, pdf_images)