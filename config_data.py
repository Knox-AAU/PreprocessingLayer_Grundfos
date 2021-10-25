import os
from os import path
from typing import List

config = {}
env_suffix = "GRUNDFOS_"

def check_env(enviroment_var_name): #, default_folder_path
    if enviroment_var_name not in os.environ:
        #if path.isdir(default_folder_path):
        #    create_output_folder = input("Enviroment variable '" + enviroment_var_name + "' does not exist. Do you want to use the default value '" + default_folder_path + "'? (anwser 'yes' or 'no')\n> ").lower()
        #else:
        #    create_output_folder = "no"
        #
        #if create_output_folder == "yes" or create_output_folder == "y":
        #    os.environ[enviroment_var_name] = default_folder_path
        #else:
        while (enviroment_var_name not in os.environ):
            user_defined_output_folder = input("Pleace defind a value for '" + enviroment_var_name + "': (only for this session)\n> ")
            if path.isdir(user_defined_output_folder):
                os.environ[enviroment_var_name] = user_defined_output_folder
                config[enviroment_var_name[len(env_suffix):]] = user_defined_output_folder
            else:
                print("Sorry, what path does not exist. Please check for syntax errors, and that the folder exists.")
        print("")

def set_config_data_from_envs():
    config["PROJECT_ROOT_PATH"] = os.getcwd()
    for env, path in os.environ.items():
        if (env.startswith(env_suffix)):
            config[env[len(env_suffix):]] = path

def check_config(required: List[str] = None):
    #check_env("GRUNDFOS_INPUT_FOLDER", "/srv/data/grundfosarchive/")
    #check_env("GRUNDFOS_INVALID_INPUT_FOLDER", "/srv/data/grundfosarchive/invalid")
    #check_env("GRUNDFOS_OUTPUT_FOLDER", "/srv/data/processed/grundfos/")
    for env in required:
        check_env(env)

if __name__ == "__main__":
    check_config()
else:
    set_config_data_from_envs()