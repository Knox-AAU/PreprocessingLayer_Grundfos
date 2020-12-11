from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
import os
import text_extraction_example

# Make an object which holds information about the content
# It should be expanded and iterated upon when we have more work
class Manual(Model):
    publisher: str
    published_at: str
    title: str
    sections: []

    def __init__(self, values: dict = None, **kwargs):
        values = values if values is not None else kwargs
        self.text = []
    
    #def __init__(self, file_sections):
        #self.sections = file_sections

class Section():
    header: str
    pages: []
    paragraphs: []

    def __init__(self, section_header, section_span, file_paragraphs):
        self.header = section_header
        self.pages = section_span
        self.paragraphs = file_paragraphs

class Paragraph():
    pages: []
    text: str
    
    def __init__(self, paragraph_span, file_text):
        self.pages = paragraph_span
        self.text = file_text

class Illustration():
    pages: str
    path: str

class Figure(Illustration):

    def __init__(self, page_span, figure_path):
        self.pages = page_span
        self.path = figure_path

class Table(Illustration):

    def __init__(self, page_span, table_path):
        self.pages = page_span
        self.path = table_path


def main():
    # Create object and properties
    # Here we should use our tools to crate the objects. 
    text = text_extraction_example.extractLines()
    file_string_array = []
    for string in text:
        file_string_array.append(string)

    file_sections = Section("header_here", [1,2], Paragraph([1,2], file_string_array))
    export_able_object = Model()
    export_able_object.publisher = "Grundfos A/S"
    export_able_object.published_at = "Somewhere"
    export_able_object.title = "Some pump"
    export_able_object.sections = file_sections
 
    # Generate
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", generated_at="idk", version="1.0"), "/manuals.schema.json")
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'output.json')

    # Serialize object to json
    with open(filename, 'w', encoding='utf-8') as outfile:
        handler.write_json(export_able_object, outfile)
    print("Json written to output.json")

    # Deserialize json to object
    #with open(filename, 'r', encoding='utf-8') as json_file:
    #obj: Wrapper = handler.read_json(json_file)
    #print("Json read from output.json")

if __name__ == "__main__":
    main()
