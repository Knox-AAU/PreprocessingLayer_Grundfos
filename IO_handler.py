from binascii import b2a_hex
import argparse
import os
import shutil
import time

start_time = time.time()

def folder_prep(output:str = "tmp", clean:bool = False):
    tmp_folder = os.path.join(output, "tmp")
    if clean is True:
        shutil.rmtree(output)
        os.mkdir(output)
    # raise IOError in case an output already excists in the selected directory and a clean run is not selected
    elif os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)
    # make new directories and print time
    mkdirs(tmp_folder)

def mkdirs(temporary_folder: str):
    # Makes the output directory with sub-folders
    os.mkdir(temporary_folder)
    os.mkdir(os.path.join(temporary_folder, 'images'))
    os.mkdir(os.path.join(temporary_folder, 'images_annotated'))
    os.mkdir(os.path.join(temporary_folder, 'figures'))
    os.mkdir(os.path.join(temporary_folder, 'line_cords'))

def initialize():
    # Arguments
    argparser = argparse.ArgumentParser(description="WIP")
    argparser.add_argument("-i", "--input", action="store", default=os.path.join(os.getcwd(), 'src'), help="Path to input folder")
    argparser.add_argument("-o", "--output", action="store", default=os.path.join(os.getcwd(), 'out'), help="Path to output folder")
    argparser.add_argument("-c", "--clean", action="store", type=bool, default=False, help="Activate nice mode.")
    args = argparser.parse_args()

    folder_prep(args.output)

def get_file_extension(stream_first_4_bytes):
    # Gets the hex bytecode for the first 4 hexadecimals of the 
    bytes_as_hex = b2a_hex(stream_first_4_bytes).decode()
    # Save file extension and return it
    if bytes_as_hex.startswith('ffd8'):
        return '.jpeg'
    elif bytes_as_hex == '89504e47':
        return ',png'
    elif bytes_as_hex == '47494638':
        return '.gif'
    elif bytes_as_hex.startswith('424d'):
        return '.bmp'

if __name__ == '__main__':
    initialize()



    

