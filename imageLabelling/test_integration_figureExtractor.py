import unittest
import json
from figureExtractor import * 

def testFileName():
    #arrange
    figureExtractor = FigureExtractor('tests/test_json', 'tests/TEST_OUTPUT_FIG', 'tests/TEST_OUTPUT_DATA', 'tests/TEST_OUTPUT_PRUNED', '')
    
    #testCases = [("grundfos.json", "grundfos"), ("hel-lo.world", "hel-lo"), ("_hello.world", "_hello")]
    
    #act
    figureExtractor.get_figure_data()
    figureExtractor.labelFigures(3)
    print("test")
    
    #assert
    with open("tests/TEST_OUTPUT_PRUNED/Grundfosliterature-2405.json", encoding="utf8") as actualData:
        actualJSON = json.load(actualData, encoding="utf8")
        actualJSON = json.dumps(actualJSON, sort_keys=True)
        
    with open("tests/test_json/Grundfosliterature-2405.json", encoding="utf8") as expectedData:
        expectedJSON = json.load(expectedData, encoding="utf8")
        expectedJSON = json.dumps(expectedJSON, sort_keys=True)
    
    assert actualJSON == expectedJSON
    
    
        

