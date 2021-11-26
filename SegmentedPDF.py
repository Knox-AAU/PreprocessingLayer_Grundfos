class SegPDF:
    PDFtitle = ""
    PDFSubTitle = ""
    Text = ""
    OriginalPath = ""

    def __init__(self):
        self.Sections = []

    def add_section(self, section):
        self.Sections.append(section)


class Section:
    Title = ""
    Text = ""
    StartingPage = None
    EndingPage = None

    def __init__(self):
        self.Sections = []

    def add_section(self, section):
        self.Sections.append(section)
