import argparse
import os


def defaultArguments(description:str):
    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument(
        "-i",
        "--input",
        type=str,
        action="store",
        metavar="INPUT",
        help="Path to input folder.",
    )
    argparser.add_argument(
        "-o",
        "--output",
        type=str,
        action="store",
        metavar="OUTPUT",
        help="Path to output folder.",
    )
    argparser.add_argument(
        "-ii",
        "--invalid_input",
        type=str,
        action="store",
        metavar="INVALID_INPUT",
        default="invalid_input",
        help="Path to invalid input folder.",
    )
    argparser.add_argument(
        "-a",
        "--accuracy",
        type=float,
        default=0.7,
        metavar="A",
        help="Minimum threshold for the prediction accuracy. Value between 0 to 1.",
    )
    argparser.add_argument(
        "-m",
        "--machine",
        action="store_true",
        help="Enable machine intelligence crossreferencing.",
    )  # NOTE: Could be merged with accuracy arg
    argparser.add_argument(
        "-t",
        "--temporary",
        action="store_true",
        default=False,
        help="Keep temporary files",
    )
    argparser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        default=False,
        help="Clear output folder before running.",
    )
    argparser.add_argument(
        "-s",
        "--schema",
        type=str,
        action="store",
        default="/schema/manuals_v1.3.schema.json",
        help="Path to json schema.",
    )
    argparser.add_argument(
        "-d",
        "--download",
        action="store_true",
        default=False,
        help="Downloads Grundfos data to input folder.",
    )
    
    return argparser

def defaultEnviromentVariables(argv, config_data):
    # Overwrite environment variables for this session, if program flags exists.
    if argv.input:
        os.environ["GRUNDFOS_INPUT_FOLDER"] = str(os.path.abspath(argv.input))
    if argv.invalid_input:
        os.environ["GRUNDFOS_INVALID_INPUT_FOLDER"] = str(
            os.path.abspath(argv.invalid_input)
        )
    if argv.output:
        os.environ["GRUNDFOS_OUTPUT_FOLDER"] = str(os.path.abspath(argv.output))
    config_data.set_config_data_from_envs()