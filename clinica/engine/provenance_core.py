from clinica.utils.stream import cprint
from .provenance_config import Configuration
import json
import os


class ProvenanceContext(object):
    def __init__(self, prov_data):
        self.prov_data = prov_data
        self.config = Configuration()

    @staticmethod
    def is_prov(file_path):
        """
        Check if the given file is a valid provenance json-ld
        """
        # TODO: check the file extension and content
        return True

    def read_prov_file(self, file_path):
        """
        Add the current file to the active provenance dictionary
        """
        try:
            with open(file_path) as fp:
                if self.is_prov(fp):
                    local_data = json.load(fp)
                    self.append_prov_dict(local_data)
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

    def discover(self, path):
        """
        Discover all the prov files in a given path and add to active dict
        """
        for root, dirs, files in os.walk(".", topdown=False):
            for file in files:
                # TODO: update file_path
                file_path = file
                if self.is_prov(file_path):
                    self.add(file_path)

    def append_prov_dict(self, local_data):
        """
        Append a specific prov data to the global prov dict
        """

        self.prov_data["records"]["Entity"].append(local_data["records"]["Entity"])
        self.prov_data["records"]["Agent"].append(local_data["records"]["Agent"])
        self.prov_data["records"]["Activity"].append(local_data["records"]["Activity"])
        return

    def update_activities(command, local_data):
        # TODO: update the acitivities dict
        return local_data

    def update_agents(command, local_data):
        # TODO: update the acitivities dict
        return local_data

    def update_entities(command, local_data):
        # TODO: update the acitivities dict
        return local_data

    def update_prov_file(self, command, file_path):
        """
        Update provenance file with result of new command
        """
        local_data = {}
        self.update_activities(command, local_data)
        self.update_agents(command, local_data)
        self.update_entities(command, local_data)
        self.write_prov_file(local_data, file_path)

        return local_data

    def create_prov_file(command, path):
        """
        Create new provenance file based on command
        """
        # TODO: create a json-ld object next to the file and add it to the active prov object
        return

    def execute_and_trace(self, command, file_path):
        """
        Record the current activity to the provenance file and update active dict
        """
        if self.is_prov(file_path):
            if self.is_valid(command, file_path):
                local_dict = self.update_prov_file(command, file_path)
                self.append_prov_dict(local_dict)
        else:
            local_dict = self.create_prov_file(command, file_path)
            self.append_prov_dict(local_dict)

    def is_valid(self, command, file_path):
        """
        Check the command is valid on the data being run
        """
        # TODO: handle the different use cases
        return True
