from clinica.utils.stream import cprint

import json
import os
import functools

from pathlib import Path


def init_prov(func):
    @functools.wraps(func)
    def init_wrapper(self, **kwargs):
        # call the constructor for the pipeline and check return code
        ret = func(self, **kwargs)
        # Postprocessing: discover the provenance files and add them to the active context

        return ret

    return init_wrapper


def provenance(func):
    def run_wrapper(self, **kwargs):

        # Discovering provenance context
        command, file_path = discover(kwargs.get("path"))
        validate_command(command, file_path)

        # Run the pipeline
        func()

        # Postprocessing provenance
        register_prov(command, file_path)

    return run_wrapper


def is_prov(file_path):
    """
    Check if the given file is a valid provenance json-ld
    """
    json_ld = Path(file_path)
    if json_ld.is_file():
        with open(json_ld, "r") as fp:
            json_ld_data = fp.readlines()
            if validateJSON(json_ld_data):
                return True
    return False


def discover(file_path):
    """
    Discover all the prov files in a given path and add to active dict
    """
    for root, dirs, files in os.walk(".", topdown=False):
        for file in files:
            # TODO: update file_path
            file_path = file
            if is_prov(file_path):
                add_prov_file(file_path)
            # TODO else: return empty provenance info for file


def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True


def add_prov_file(file_path):
    """
    Add the current file to the active provenance dictionary
    """
    try:
        with open(file_path) as fp:
            if is_prov(fp):
                local_data = json.load(fp)
                append_prov_dict(local_data)
                # TODO: return subset of data
                return local_data
            else:
                return {}
    except FileNotFoundError as e:
        cprint("No such file or directory")


def write_prov_file(local_data, file_path):
    """
    Write the dictionary data to the file_path
    """
    # TODO: update the json-ld file associated with the file_path with the local_data
    return file_path


def append_prov_dict(local_data):
    """
    Append a specific prov data to the global prov dict
    """
    prov_data["records"]["Entity"].append(local_data["records"]["Entity"])
    prov_data["records"]["Agent"].append(local_data["records"]["Agent"])
    prov_data["records"]["Activity"].append(local_data["records"]["Activity"])
    return


def update_activities(command, local_data):
    # TODO: update the acitivities dict
    return local_data


def update_agents(command, local_data):
    # TODO: update the activities dict
    return local_data


def update_entities(command, local_data):
    # TODO: update the acitivities dict
    return local_data


def update_prov_file(self, command, file_path):
    """
    Update provenance file with result of new command
    """
    local_data = {}
    update_activities(command, local_data)
    update_agents(command, local_data)
    update_entities(command, local_data)
    write_prov_file(local_data, file_path)

    return local_data


def create_prov_file(command, path):
    """
    Create new provenance file based on command
    """
    # TODO: create a json-ld object next to the file and add it to the active prov object
    return


def register_prov(command, file_path):
    """
    Record the current activity to the provenance file and update active dict
    """
    if is_prov(file_path):
        local_dict = update_prov_file(command, file_path)
        append_prov_dict(local_dict)
    else:
        local_dict = create_prov_file(command, file_path)
        append_prov_dict(local_dict)


def validate_command(command, file_path):
    """
    Check the command is valid on the data being run
    """
    # TODO: handle the different use cases
    return True
