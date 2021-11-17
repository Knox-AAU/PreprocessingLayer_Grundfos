import argparse
import os
import unittest

import config_data
import segment as seg


class SegmentationTests(unittest.TestCase):
    def test_if_file_is_too_big_unit(self):
        args = ["-c", "-iinput_timer", "-ooutput_timer"]

        argparser = argparse.ArgumentParser(description="Segments pdf documents.")
        argparser.add_argument("-i", "--input", type=str, action="store", metavar="INPUT", help="Path to input folder.")
        argparser.add_argument("-o", "--output", type=str, action="store", metavar="OUTPUT",
                               help="Path to output folder.")
        argparser.add_argument("-ii", "--invalid_input", type=str, action="store", metavar="INVALID_INPUT",
                               help="Path to invalid input folder.")
        argparser.add_argument("-a", "--accuracy", type=float, default=0.7, metavar="A",
                               help="Minimum threshold for the prediction accuracy. Value between 0 to 1.")
        argparser.add_argument("-m", "--machine", action="store_true",
                               help="Enable machine intelligence crossreferencing.")  # NOTE: Could be merged with accuracy arg
        argparser.add_argument("-t", "--temporary", action="store_true", default=False, help="Keep temporary files")
        argparser.add_argument("-c", "--clean", action="store_true", default=False,
                               help="Clear output folder before running.")
        argparser.add_argument("-s", "--schema", type=str, action="store", default="/schema/manuals_v1.1.schema.json",
                               help="Path to json schema.")
        argparser.add_argument("-d", "--download", action="store_true", default=False,
                               help="Downloads Grundfos data to input folder.")
        argv = argparser.parse_args(args)

        if argv.input:
            os.environ["GRUNDFOS_INPUT_FOLDER"] = str(os.path.abspath(argv.input))
        if argv.invalid_input:
            os.environ["GRUNDFOS_INVALID_INPUT_FOLDER"] = str(os.path.abspath(argv.invalid_input))
        if argv.output:
            os.environ["GRUNDFOS_OUTPUT_FOLDER"] = str(os.path.abspath(argv.output))

        config_data.set_config_data_from_envs()
        with self.assertWarns(UserWarning):
            seg.segment_documents(argv)

    def test_segments_integrations(self):
        args = ["-c", "-iinput_segments", "-ooutput_timer"]

        argparser = argparse.ArgumentParser(description="Segments pdf documents.")
        argparser.add_argument("-i", "--input", type=str, action="store", metavar="INPUT", help="Path to input folder.")
        argparser.add_argument("-o", "--output", type=str, action="store", metavar="OUTPUT",
                               help="Path to output folder.")
        argparser.add_argument("-ii", "--invalid_input", type=str, action="store", metavar="INVALID_INPUT",
                               help="Path to invalid input folder.")
        argparser.add_argument("-a", "--accuracy", type=float, default=0.7, metavar="A",
                               help="Minimum threshold for the prediction accuracy. Value between 0 to 1.")
        argparser.add_argument("-m", "--machine", action="store_true",
                               help="Enable machine intelligence crossreferencing.")  # NOTE: Could be merged with accuracy arg
        argparser.add_argument("-t", "--temporary", action="store_true", default=False, help="Keep temporary files")
        argparser.add_argument("-c", "--clean", action="store_true", default=False,
                               help="Clear output folder before running.")
        argparser.add_argument("-s", "--schema", type=str, action="store", default="/schema/manuals_v1.1.schema.json",
                               help="Path to json schema.")
        argparser.add_argument("-d", "--download", action="store_true", default=False,
                               help="Downloads Grundfos data to input folder.")
        argv = argparser.parse_args(args)

        if argv.input:
            os.environ["GRUNDFOS_INPUT_FOLDER"] = str(os.path.abspath(argv.input))
        if argv.invalid_input:
            os.environ["GRUNDFOS_INVALID_INPUT_FOLDER"] = str(os.path.abspath(argv.invalid_input))
        if argv.output:
            os.environ["GRUNDFOS_OUTPUT_FOLDER"] = str(os.path.abspath(argv.output))

        config_data.set_config_data_from_envs()

        with self.assertWarns(Warning):
            seg.segment_documents(argv)



if __name__ == '__main__':
    unittest.main()
