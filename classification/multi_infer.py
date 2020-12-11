"""
This module allow MI-inference on multiple files.
"""
import os
import argparse
import infer

def multi_infer(in_dir: str, out_dir: str):
    """
    Runs inference on all images in a specified directory
    """
    for file in os.listdir(in_dir,):
        if file.endswith(".png"):
            infer.infer_image_with_mask(os.path.join(in_dir,file), out_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Path to input directory")
    parser.add_argument("output", type=str, help="Path to output directory")
    args = parser.parse_args()

    multi_infer(args.input, args.output)
    exit()
