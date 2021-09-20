import json
import functools
from os import read

from pathlib import Path


def provenance(func):
    from .provenance_utils import get_files_list

    @functools.wraps(func)
    def run_wrapper(self, **kwargs):

        pipeline_fullname = self.fullname
        in_files_paths, out_files_paths = get_files_list(self, pipeline_fullname)

        prov_input = get_prov(files_paths=in_files_paths)
        prov_output = get_prov(files_paths=out_files_paths)

        validate_command(prov_input, prov_output)

        # Run the pipeline
        ret = func(self)

        # TODO: register_prov(command, file_path)

        return ret

    return run_wrapper


def get_prov(files_paths):
    """
    Return a dictionary with the provenance info related to the files in the files_paths
    """
    prov_data = {"records": {"Entity": [], "Agent": [], "Activity": []}}
    for path in files_paths:
        prov_record = read_prov(path)
        if prov_record:
            prov_data = append_prov_dict(prov_data, prov_record)

    return prov_data


def read_prov(file_path):
    """
    Check if the given file is a valid provenance json-ld
    """
    json_ld = Path(file_path)
    if json_ld.suffix == ".json-ld" or json_ld.suffix == ".json":
        with open(json_ld, "r") as fp:
            json_ld_data = json.load(fp)
            return json_ld_data
    return False


def get_command(self, prov_context):
    """
    Read the user command and save information in a dict
    """
    import sys

    new_agent = get_agent()
    # TODO see if the entities already exist in the context, otherwise create them
    new_entity = get_entity(self)
    new_activity = get_activity(self, new_agent["@id"], new_entity["@id"])

    return {"Agent": new_agent, "Activity": new_activity, "Entity": new_entity}


# def get_context(bids_dir):
#     """
#     Get the prov files in a given path and add to active dict
#     """

#     import os

#     prov_context = {"records": {"Entity": [], "Agent": [], "Activity": []}}
#     for root, _, files in os.walk(bids_dir, topdown=False):
#         for file in files:
#             file_path = os.path.join(root, file)
#             prov_tmp = read_prov(file_path)
#             if prov_tmp:
#                 prov_context = append_prov_dict(prov_context, prov_tmp)

#     return prov_context


def validateJSON(jsonData):
    try:
        json.loads(jsonData[0])
    except ValueError as err:
        return False
    return True


def write_prov_file(local_data, file_path):
    """
    Write the dictionary data to the file_path
    """
    # TODO: update the json-ld file associated with the file_path with the local_data
    return file_path


def append_prov_dict(prov_data, local_data):
    """
    Append a specific prov data to the global prov dict
    """
    prov_data["records"]["Entity"].append(local_data["records"]["Entity"])
    prov_data["records"]["Agent"].append(local_data["records"]["Agent"])
    prov_data["records"]["Activity"].append(local_data["records"]["Activity"])
    return prov_data


def get_agent():
    import clinica
    from .provenance_utils import get_agent_id

    agent_version = clinica.__version__
    agent_label = clinica.__name__
    agent_id = get_agent_id(agent_label + agent_version)

    new_agent = {"@id": agent_id, "label": agent_label, "version": agent_version}

    return new_agent


def get_activity(self, agent_id, entity_id):
    """
    Add the current command to the list of activities
    """
    import sys
    from .provenance_utils import get_activity_id

    activity_parameters = self.parameters
    activity_label = self.fullname
    activity_id = get_activity_id(self.fullname)
    activity_command = (sys.argv[1:],)
    activity_agent = agent_id
    activity_used_file = entity_id

    new_activity = {
        "@id": activity_id,
        "label": activity_label,
        "command": activity_command,
        "parameters": activity_parameters,
        "wasAssociatedWith": activity_agent,
        "used": entity_id,
    }

    return new_activity


def get_entity(self, img_path):
    """
    Add the current file to the list of entities
    """
    from clinica.engine.provenance_utils import get_entity_id
    from pathlib import Path
    from clinica.utils.filemanip import extract_image_ids

    entity_id = get_entity_id(img_path)
    entity_label = Path(img_path).name
    entity_path = img_path

    new_entity = {
        "@id": entity_id,
        "label": entity_label,
        "atLocation": entity_path,
        "wasGeneratedBy": "",
    }

    return new_entity


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


def validate_command(prov_context, prov_command):
    """
    Check the command is valid on the data being run
    """

    return True
