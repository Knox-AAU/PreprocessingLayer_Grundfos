import argparse
import os
import shlex
import unittest

import config_data
import segment as seg
from pathlib import Path
from defaultProgramArguments import defaultArguments, defaultEnviromentVariables


class SegmentationTests(unittest.TestCase):
    def test_segmentation(self):
        testFolder = Path("tests/data")
        inputFolder = str(testFolder / "input")
        outputFolder = str(testFolder / "output")

        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)

        args = "-c -i '" + inputFolder + "' -o '" + outputFolder + "'"
        print(args)
        argv = defaultArguments("Segments pdf documents.").parse_args(shlex.split(args))
        defaultEnviromentVariables(argv, config_data)

        config_data.check_config(["GRUNDFOS_INPUT_FOLDER", "GRUNDFOS_OUTPUT_FOLDER"])

        seg.Segmentation(argv)


if __name__ == "__main__":
    unittest.main()
