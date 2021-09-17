def get_files_list(self):
    """
    Calls clinica_file_reader with the appropriate extentions
    """
    from clinica.utils.inputs import clinica_file_reader
    from clinica.utils.input_files import T1W_NII

    pipeline = self.fullname
    if pipeline == "t1-linear":
        image_files = clinica_file_reader(
            self.subjects, self.sessions, self.bids_directory, T1W_NII
        )
    return image_files


def is_entity_tracked(prov_context, entity_id):
    flag_exists = next(
        (
            True
            for item in prov_context["records"]["Entity"]
            if item["@id"] == entity_id
        ),
        False,
    )
    return flag_exists


def is_agent_tracked(prov_context, agent_id):
    flag_exists = next(
        (True for item in prov_context["records"]["Agent"] if item["@id"] == agent_id),
        False,
    )
    return flag_exists


def is_activity_tracked(prov_context, activity_id):
    flag_exists = next(
        (
            True
            for item in prov_context["records"]["Activity"]
            if item["@id"] == activity_id
        ),
        False,
    )
    return flag_exists


def get_entity_id(file_path):
    from pathlib import Path

    entity_id = Path(file_path).with_suffix("").name
    return entity_id


def get_activity_id(pipeline_name):
    return "clin:" + pipeline_name


def get_agent_id(agent_name):
    return "clin:" + agent_name