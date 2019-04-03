"""
Module dealing with interacting with Nextflow
"""

import logging
import configparser
import datetime
from pathlib import Path

from sequencing_report_service.exceptions import NextflowConfigError

log = logging.getLogger(__name__)


# pylint: disable=R0903
# Intentionally disabling R0903 too-few-public-methods error to allow for NextflowCommandGenerator
class NextflowCommandGenerator():
    """
    This is a factory to generate commands to start Nextflow. It assumes
    that it has a setup which contains a value called RUNFOLDER_REPLACE.
    This value can then be substituted when generating commands to run
    on different runfolders.
    """

    def __init__(self, config_dict):
        """
        :param: config_dict a dict containing the configuration for the class
        """
        try:
            self._cmd = ['nextflow', '-config', config_dict['nf_config'], 'run',
                         config_dict['main_workflow_path']]
            if not config_dict.get('parameters'):
                raise NextflowConfigError("The parameters to the nextflow job was empty.")
            self._raw_params = config_dict['parameters']
        except KeyError as exc:
            log.error(exc)
            raise NextflowConfigError(exc)
        except NextflowConfigError as exc:
            log.error(exc)
            raise exc

    def _construct_nf_param_list(self, runfolder_path):
        """
        Read the parameters part of the dict and use it to generate a list
        of parameters and their values.
        :param: runfolder_path path to the runfolder to process
        """

        # This uses the variable interpolation capablities of the ConfigParser
        # to replace variables setup in the config. Creating a new dict is necessary
        # to conform to the standard format required by the Python config parser.
        # /JD 2018-04-03
        defaults = {'runfolder_path': str(runfolder_path),
                    'runfolder_name': runfolder_path.name,
                    'current_year': datetime.datetime.now().year}
        conf = configparser.ConfigParser(defaults=defaults, interpolation=configparser.ExtendedInterpolation())
        params_as_conf_dict = {'nextflow_config': self._raw_params}
        conf.read_dict(params_as_conf_dict)

        lst = []
        for key, value in conf['nextflow_config'].items():
            # This check is necessary to ensure that the default values
            # are not also output here. /JD 2019-04-03
            if key in self._raw_params.keys():
                lst += [f"--{key}", f"{value}"]

        return lst

    def command(self, runfolder):
        """
        Return a list containing the command to run with the specified runfolder
        inserted at the configured path.
        :param: runfolder path the the runfolder to run command on.
        """
        if not isinstance(runfolder, Path):
            runfolder = Path(runfolder)
        cmd = self._cmd + self._construct_nf_param_list(runfolder)
        log.debug("Generated command: %s", cmd)
        return cmd
