"""
Module dealing with interacting with Nextflow
"""

import copy
import logging
import datetime
from pathlib import Path
import json
import jsonschema
import yaml

from sequencing_report_service.exceptions import NextflowConfigError

log = logging.getLogger(__name__)


def interpolate_variables(config, defaults):
    """
    Interpolate variables from the `config` dictionary` with the values from
    `default`: values defined as `{variable_name}` will be replaced by the
    value at `variable_name` in the `default` dictionary.

    Parameters
    ----------
    config: dict
        dict where values need to be interpolated
    defaults: dict
        dict containing the new values

    Returns
    -------
    dict
        dictionaries with interpolated variables
    """
    config = copy.deepcopy(config)
    try:
        for section in ["environment", "parameters"]:
            for key, value in config[section].items():
                config[section][key] = value.format(**defaults)
    except KeyError:
        # This may happen if some format strings contain keys that are not in
        # `defaults`.
        log.exception('')
        raise

    return config


class NextflowCommandGenerator():
    """
    A class to generate Nextflow commands according to parameters specified in
    a configuration file. The file should be named after the pipeline eg.
    `pipeline_name.yml`.

    Attributes
    -----------
    config_dir: str
        path were the pipeline config files are located
    """
    def __init__(self, config_dir):
        self.config_dir = Path(config_dir)

    def command(self, runfolder_path, pipeline="seqreports"):
        """
        Returns nextflow command with parameter as specified in the
        corresponding config file.

        Parameters
        ----------
        runfolder_path: str
            path to the runfolder to process
        pipeline: str
            name of the pipeline to use
        """
        runfolder_path = Path(runfolder_path)

        try:
            with open(self.config_dir / f"{pipeline}.yml", "r") as config_file:
                config = yaml.safe_load(config_file.read())
            with open(self.config_dir / "schema.json", "r") as pipeline_config_schema:
                schema = json.load(pipeline_config_schema)
            jsonschema.validate(config, schema)
        except (FileNotFoundError, jsonschema.ValidationError):
            log.exception('')
            raise

        config = interpolate_variables(
            config,
            {
                'runfolder_path': str(runfolder_path),
                'runfolder_name': runfolder_path.name,
                'current_year': datetime.datetime.now().year
            }
        )

        env_config = config["environment"]

        cmd = [
            'nextflow',
            '-config', config['nf_config'],
            'run', config['main_workflow_path'],
            '-profile', config['nf_profile'],
        ]

        cmd += [
            arg
            for key, value in config["parameters"].items()
            for arg in [f"--{key}", f"{value}"]
        ]

        log.debug("Generated command: %s", cmd)
        return {'command': cmd, 'environment': env_config}
