import os
import shutil
from os import path
import config_data
from config_data import config

def move_invalid_pdf_files():
    number_of_files = len(os.listdir(config["INPUT_FOLDER"]))
    file = 0
    invalid_files = 0
    for filename in os.listdir(config["INPUT_FOLDER"]):
        file += 1
        input_file_path = os.path.join(config["INPUT_FOLDER"], filename)
        invalid_input_file_path = os.path.join(config["INVALID_INPUT_FOLDER"], filename)
        id = filename[len("Grundfosliterature-"):len(filename)-len(".pdf")]
        json_output_path = os.path.join(config["OUTPUT_FOLDER"],
                           "Grundfosliterature-" + id,
                           "Grundfosliterature-" + id + "_output.json")
        if path.isfile(json_output_path) == False:
            invalid_files += 1
            print("(" + str(file) + " of " + str(number_of_files) + ") \t" +
                  "Moving invalid file: " + filename + "    ", end='\r')
            shutil.move(input_file_path, invalid_input_file_path)
    
    print("")
    if (invalid_files == 0):
        print("No invalid files found")
    else:
        print(str(invalid_files) + " invalid files moved")

if __name__ == "__main__":
    config_data.check_config(["GRUNDFOS_INPUT_FOLDER",
                              "GRUNDFOS_INVALID_INPUT_FOLDER",
                              "GRUNDFOS_OUTPUT_FOLDER"])
    for item in config:
        print(item, ": ", config[item])
    move_invalid_pdf_files()