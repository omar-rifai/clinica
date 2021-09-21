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

        prov_context = get_context(files_paths=in_files_paths)
        prov_command = get_command(self, prov_context, files_paths=out_files_paths)

        validate_command(prov_context, prov_command)

        # Run the pipeline
        ret = func(self)

        # TODO: register_prov(command, file_path)

        return ret

    return run_wrapper


def get_context(files_paths):
    """
    Return a dictionary with the provenance info related to the files in the files_paths
    """
    prov_data = {"Entity": [], "Agent": [], "Activity": []}
    for path in files_paths:
        prov_record = read_prov(path)
        if prov_record:
            prov_data = append_prov_dict(prov_data, prov_record)

    return prov_data


def read_prov(file_path):
    """
    Check if the given file is a valid provenance json-ld
    """

    # remove one or multiple extensions from the file
    file_path = Path(file_path)
    while file_path.suffix != "":
        file_path = file_path.with_suffix("")

    associated_jsonld = file_path.with_suffix(".jsonld")
    if associated_jsonld.exists():
        with open(associated_jsonld, "r") as fp:
            json_ld_data = json.load(fp)
            return json_ld_data
    return False


def get_command(self, prov_context, files_paths):
    """
    Read the user command and save information in a dict
    """
    import sys

    new_agent = get_agent()
    if prov_context["Entity"]:
        new_activity = get_activity(self, new_agent["@id"], prov_context["Entity"])

    return {"Agent": [new_agent], "Activity": [new_activity], "Entity": []}


def write_prov_file(prov_command, files_paths):
    """
    Write the dictionary data to the file_path
    """

    for path in files_paths:
        new_entity = get_entity(path)
        record = {
            "Agent": prov_command["Agent"],
            "Activity": prov_command["Activity"],
            "Entity": new_entity,
        }
    # TODO: write the prov file
    return record


def append_prov_dict(prov_data, local_data):
    """
    Append a specific prov data to the global prov dict
    """
    prov_data["Entity"].extend(local_data["Entity"])
    prov_data["Agent"].extend(local_data["Agent"])
    prov_data["Activity"].extend(local_data["Activity"])
    return prov_data


def get_agent():
    import clinica
    from .provenance_utils import get_agent_id

    agent_version = clinica.__version__
    agent_label = clinica.__name__
    agent_id = get_agent_id(agent_label + agent_version)

    new_agent = {"@id": agent_id, "label": agent_label, "version": agent_version}

    return new_agent


def get_activity(self, agent_id, entities):
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
    activity_used_files = [e["@id"] for e in entities]

    new_activity = {
        "@id": activity_id,
        "label": activity_label,
        "command": activity_command,
        "parameters": activity_parameters,
        "wasAssociatedWith": activity_agent,
        "used": activity_used_files,
    }

    return new_activity


def get_entity(img_path):
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

    return local_data


def create_prov_file(command, path):
    """
    Create new provenance file based on command
    """
    # TODO: create a json-ld object next to the file and add it to the active prov object
    return


def validate_command(prov_context, prov_command):
    """
    Check the command is valid on the data being run
    """
    flag = True
    new_activity_id = prov_command["Activity"][0]["@id"]
    new_agent_id = prov_command["Agent"][0]["@id"]

    for entity in prov_context["Entity"]:
        old_activity_id = entity["wasGeneratedBy"]
        if old_activity_id:
            ptr_activity = next(
                item
                for item in prov_context["Activity"]
                if item["@id"] == old_activity_id
            )
            old_agent_id = ptr_activity["wasAssociatedWith"]
            flag and is_valid(
                (old_activity_id, old_agent_id), (new_activity_id, new_agent_id)
            )
    return True


def is_valid(old, new):
    return True