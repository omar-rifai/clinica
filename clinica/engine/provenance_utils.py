from clinica.utils.input_files import T1W_NII


def get_files_list(self, pipeline_fullname):
    """
    Calls clinica_file_reader with the appropriate extentions
    """
    from clinica.utils.inputs import clinica_file_reader
    import clinica.utils.input_files as cif

    # retrieve all the data dictionaries from the input_files module
    input_dicts = {
        k: v
        for k, v in vars(cif).items()
        if isinstance(v, dict)
        and "input_to" in v.keys()
        and pipeline_fullname in v["input_to"]
    }

    output_dicts = {
        k: v
        for k, v in vars(cif).items()
        if isinstance(v, dict)
        and "output_from" in v.keys()
        and pipeline_fullname in v["output_from"]
    }

    for elem in input_dicts:
        in_files = clinica_file_reader(
            self.subjects, self.sessions, self.bids_directory, input_dicts[elem]
        )
    for elem in output_dicts:
        out_files = clinica_file_reader(
            self.subjects,
            self.sessions,
            self.bids_directory,
            output_dicts[elem],
            raise_exception=False,
        )

    return in_files, out_files


def is_entity_tracked(prov_context, entity_id):
    flag_exists = next(
        (True for item in prov_context["Entity"] if item["@id"] == entity_id),
        False,
    )
    return flag_exists


def is_agent_tracked(prov_context, agent_id):
    flag_exists = next(
        (True for item in prov_context["Agent"] if item["@id"] == agent_id),
        False,
    )
    return flag_exists


def is_activity_tracked(prov_context, activity_id):
    flag_exists = next(
        (True for item in prov_context["Activity"] if item["@id"] == activity_id),
        False,
    )
    return flag_exists


def is_empty(prov):

    return prov["Entity"]


def get_entity_id(file_path):
    from pathlib import Path

    entity_id = Path(file_path).with_suffix("").name
    return entity_id


def get_activity_id(pipeline_name):
    return "clin:" + pipeline_name


def get_agent_id(agent_name):
    return "clin:" + agent_name