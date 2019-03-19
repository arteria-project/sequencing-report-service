"""
Module dealing with interacting with Nextflow
"""

import logging

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
                         config_dict['repo'], '-latest', '-r', config_dict['pipeline_version']]
            self._params = self._read_parameters(config_dict['parameters'])
        except KeyError as exc:
            log.error(exc)
            raise NextflowConfigError(exc)
        except NextflowConfigError as exc:
            log.error(exc)
            raise exc

    @staticmethod
    def _read_parameters(parameters_dict):
        """
        Read the parameters part of the dict and use it to generate a list
        of parameters and their values.
        :param: parameters_dict dict of param -> value
        :raises: NextflowConfigError
        """
        if not parameters_dict:
            raise NextflowConfigError("The parameters to the nextflow job was empty. It needs a miniumum of a "
                                      "runfolder key.")
        found_runfolder_replace = False
        lst = []
        for key, value in parameters_dict.items():
            if value == 'RUNFOLDER_REPLACE':
                found_runfolder_replace = True
            lst += [f"--{key}", f"{value}"]

        if not found_runfolder_replace:
            raise NextflowConfigError("There has to be an instance of RUNFOLDER_REPLACE "
                                      "in the parameters to nextflow.")

        return lst

    def _replace_runfolder_with_path_in_params(self, runfolder_path):
        """
        Inspect the configured Nextflow parameters and replace the RUNFOLDER_REPLACE
        value with the path to the runfolder.
        :param: runfolder_path path to the runfolder
        """
        return [w.replace('RUNFOLDER_REPLACE', runfolder_path) for w in self._params]

    def command(self, runfolder):
        """
        Return a list containing the command to run with the specified runfolder
        inserted at the configured path.
        :param: runfolder path the the runfolder to run command on.
        """
        cmd = self._cmd + self._replace_runfolder_with_path_in_params(runfolder)
        log.debug("Generated command: %s", cmd)
        return cmd
