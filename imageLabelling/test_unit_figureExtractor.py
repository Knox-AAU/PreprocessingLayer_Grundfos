import unittest
from figureExtractor import * 

def testFileName():
    #arrange
    figureExtractor = FigureExtractor('IO/INPUT_ALL', 'IO/OUTPUT_FIG', 'IO/OUTPUT_DATA', 'OUTPUT_PRUNED')
    testCases = [("grundfos.json", "grundfos"), ("hel-lo.world", "hel-lo"), ("_hello.world", "_hello")]
    
    #act
    for case in testCases:
        #assert
        assert figureExtractor.get_filename(case[0]) == case[1]

