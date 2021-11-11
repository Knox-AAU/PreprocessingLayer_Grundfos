"""
Module responsible for making the output of the segmentation. 
More specifically it is preparing data for the actual wrapper used (https://git.its.aau.dk/Knox/source-data-io)
"""

from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
from knox_source_data_io.models.publication import Article, Publication, Paragraph
import datastructure.datastructure as ds
import os
import datetime
import SegmentedPDF


def create_output(segmented_pdf: SegmentedPDF.SegPDF, pages: ds.Page, file_name, schema_path, output_path):
    """
    Creates the output to JSON using knox-source-data-io module: https://git.its.aau.dk/Knox/source-data-io
    """
    print("Creating JSON output...")

    # Create list of text-sections
    print(" Creating text section list...")
    pdf_sections = create_sections(segmented_pdf.Sections)

    # Create object for JSON
    print(" Creating JSON object...")
    export_able_object = Publication()
    export_able_object.publication = file_name.replace(".pdf", "")
    export_able_object.publisher = "Grundfos A/S"
    export_able_object.pages = len(pages)

    article = Article()
    article.headline = file_name.replace(".pdf", "") #TODO rename to manual title for example "pump cu 200"
    article.page = "1 - " + str(len(pages))

    for section in pdf_sections:
        section.extracted_from = [segmented_pdf.OriginPath]
        article.add_paragraph(section)
        
    export_able_object.add_article(article)

    # Generate
    print(" Generating JSON from schema...")
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", generated_at= str(datetime.datetime.now()), version="1.3.0"), schema_path)
    output_name = str(file_name.replace(".pdf", "") + "_output.json")
    filename = os.path.join(output_path, output_name)

    # Serialise object to json
    print(" Serialising JSON...")
    with open(filename, 'w', encoding='utf-16') as outfile:
        handler.write_json(export_able_object, outfile)

    print(".JSON output created.")

def create_sections(text_sections):
    """
    Creates the datastructure for text-sections.
    """
    sections = []
    for section in text_sections:
        visited_section = visit_subsections(section)
        if visited_section is not None:  # Do not add the section if it is "null/none"
            sections = visited_section
    return sections

def visit_subsections(node: SegmentedPDF.Section):
    """
    Recursive visitor for the sections and their subsections.
    """
    schema_sections = []
    if (node.Sections != []):
        for section in node.Sections:
            if section.StartingPage == section.EndingPage:
                page = str(section.StartingPage)
            else:
                page = str(str(section.StartingPage) + "-" + str(section.EndingPage))
            if section.Text != "":
                paragraph = Paragraph()
                paragraph.value = section.Title + ". " + section.Text 
                schema_sections.append(section)
            subsection = visit_subsections(section)
            if subsection != [] and subsection is not None:
                schema_sections = schema_sections + subsection
        return schema_sections
    return None