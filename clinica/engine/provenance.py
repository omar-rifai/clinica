from clinica.utils.stream import cprint

import json
import os
import functools

from pathlib import Path


def init_prov(func):
    @functools.wraps(func)
    def init_wrapper(self, **kwargs):
        cprint("Intializing the provenance context", lvl="warning")
        # call the constructor for the pipeline and check return code
        ret = func(self, **kwargs)
        # Postprocessing: discover the provenance files and add them to the active context
        cprint("Postprocessing for provenance", lvl="warning")
        return ret

    return init_wrapper


def provenance(func):
    @functools.wraps(func)
    def run_wrapper(self, **kwargs):
        bids_dir = self._bids_directory

        prov_context = get_context(bids_dir)
        prov_data = get_current(self)
        validate_command(prov_context, prov_data)

        print(prov_data)
        # Run the pipeline
        ret = func(self)

        # Postprocessing provenance
        # register_prov(command, file_path)
        return ret

    return run_wrapper


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


def get_current(self):
    """
    Read the current user command and save information in a dict
    """
    import sys

    prov_current = {"records": {"Entity": [], "Agent": [], "Activity": []}}
    prov_current, agent_id = update_agents(prov_current)
    prov_current, activity_id = update_activities(self, agent_id, prov_current)
    prov_current = update_entities(self, prov_current)

    return prov_current


def get_context(bids_dir):
    """
    Get the prov files in a given path and add to active dict
    """

    import os

    prov_context = {"records": {"Entity": [], "Agent": [], "Activity": []}}
    for root, _, files in os.walk(bids_dir, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            prov_tmp = read_prov(file_path)
            if prov_tmp:
                prov_context = append_prov_dict(prov_context, prov_tmp)

    return prov_context


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


def update_agents(prov_data):
    import clinica

    agent_version = clinica.__version__
    agent_label = clinica.__name__
    agent_id = "clin:" + agent_version

    new_agent = {"@id": agent_id, "label": agent_label, "version": agent_version}

    if new_agent not in prov_data["records"]["Agent"]:
        prov_data["records"]["Agent"].append(new_agent)
    return prov_data, agent_id


def update_activities(self, agent_id, prov_data):
    """
    Add the current command to the list of activities
    """
    import sys

    activity_parameters = (self.parameters,)
    activity_label = (self.fullname,)
    activity_id = ("clin:" + self.fullname,)
    activity_command = (sys.argv[1:],)
    activity_agent = (agent_id,)
    activity_used_file = ""
    new_activity = {
        "@id": activity_id,
        "label": activity_label,
        "command": activity_command,
        "parameters": activity_parameters,
        "wasAssociatedWith": activity_agent,
        "used": activity_used_file,
    }

    if new_activity not in prov_data["records"]["Activity"]:
        prov_data["records"]["Activity"].append(new_activity)

    return prov_data, activity_id


def update_entities(self, prov_data):
    """
    Add the current file to the list of entities
    """
    entity_id = ""
    entity_label = ""
    entity_path = ""
    entity_activity = ""

    new_entity = {
        "@id": "entity_id",
        "label": "entity_label",
        "atLocation": "entity_path",
        "wasGeneratedBy": "entity_activity",
    }

    if new_entity not in prov_data["records"]["Entity"]:
        prov_data["records"]["Entity"].append(new_entity)

    return prov_data


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


# TODO: retrieve list of subjects sessions from BIDS folder (function already exists)
# TODO: (MAYBE) filter list based on already existing function to check already processed in CAPS
# TODO: call clinica_file_reader(.., ..,  self._input_node.inputs) to retrieve list of input files
# TODO add the files to the entities list
