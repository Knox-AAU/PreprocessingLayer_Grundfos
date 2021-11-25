"""
Uses environment variables for config
"""
import os
from os import path
from typing import List

config = {}
env_suffix = "GRUNDFOS_"


def check_env(environment_var_name):
    if environment_var_name not in os.environ:
        while environment_var_name not in os.environ:
            user_defined_output_folder = input(
                "Please define a value for '"
                + environment_var_name
                + "': (only for this session)\n> "
            )
            if path.isdir(user_defined_output_folder):
                os.environ[environment_var_name] = str(
                    os.path.abspath(user_defined_output_folder)
                )
                config[environment_var_name[len(env_suffix) :]] = str(
                    os.path.abspath(user_defined_output_folder)
                )
            else:
                print(
                    "Sorry, that path does not exist. Please check for syntax errors, and that the folder exists."
                )
        print("")


def set_config_data_from_envs():
    config["PROJECT_ROOT_PATH"] = os.getcwd()
    for env, path in os.environ.items():
        if env.startswith(env_suffix):
            config[env[len(env_suffix) :]] = path


def check_config(required: List[str] = None):
    for env in required:
        check_env(env)


if __name__ == "__main__":
    check_config()
else:
    set_config_data_from_envs()
