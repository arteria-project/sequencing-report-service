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
        for section in [
                    "environment",
                    "pipeline_parameters",
                    "nextflow_parameters",
                ]:
            if section in config:
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

    def _get_config(
        self,
        pipeline,
        runfolder_path,
        input_samplesheet,
    ):
        """
        Fetches the config data for the given pipeline.

        This will also format keywords `{current_year}`, `{runfolder_name}`,
        `{runfolder_path}` and `{input_samplesheet}`.

        Parameters
        ----------
        pipeline: str
            name of the pipeline to use
        runfolder_path: str
            path to the runfolder to process
        input_samplesheet: str
            content of the input samplesheet

        Returns
        -------
        config: dict
       """
        try:
            with open(self.config_dir / f"{pipeline}.yml", "r") as config_file:
                config = yaml.safe_load(config_file.read())
            with open(self.config_dir / "schema.json", "r") as pipeline_config_schema:
                schema = json.load(pipeline_config_schema)
            jsonschema.validate(config, schema)
        except (FileNotFoundError, jsonschema.ValidationError):
            log.exception('')
            raise

        runfolder_path = Path(runfolder_path)
        defaults = {
            "current_year": datetime.datetime.now().year,
            "runfolder_path": str(runfolder_path),
            "runfolder_name": runfolder_path.name,
        }

        input_samplesheet = input_samplesheet or config.get("input_samplesheet", "")
        if input_samplesheet:
            try:
                input_samplesheet = input_samplesheet.format(**defaults)
            except KeyError:
                log.exception('')
                raise

            input_samplesheet_path = runfolder_path / f"{pipeline}_samplesheet.csv"
            with open(input_samplesheet_path, "w") as f:
                f.write(input_samplesheet)
            defaults["input_samplesheet"] = input_samplesheet_path

        return interpolate_variables(config, defaults)

    def command(
        self,
        pipeline,
        runfolder_path,
        input_samplesheet="",
    ):
        """
        Returns nextflow command to run the requested pipeline
        with parameter as specified in the corresponding config file.

        Parameters
        ----------
        pipeline: str
            name of the pipeline to use
        runfolder_path: str
            path to the runfolder to process
        input_samplesheet: str
            content of the input samplesheet
        """
        config = self._get_config(pipeline, runfolder_path, input_samplesheet)

        env_config = config.get("environment", {})

        cmd = [
            'nextflow',
            'run', config['main_workflow_path'],
        ]

        cmd += [
            arg
            for key, value in config.get("nextflow_parameters", {}).items()
            for arg in (
                [f"-{key}", f"{value}"]
                if value else
                [f"-{key}"]
            )
        ]

        cmd += [
            arg
            for key, value in config.get("pipeline_parameters", {}).items()
            for arg in (
                [f"--{key}", f"{value}"]
                if value else
                [f"--{key}"]
            )
        ]

        log.debug("Generated command: %s", cmd)

        return {
            'command': cmd,
            'environment': env_config,
        }
