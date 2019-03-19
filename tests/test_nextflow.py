
import pytest

from sequencing_report_service.nextflow import NextflowCommandGenerator, NextflowConfigError


def test_command():
    config = {'repo': 'Molmed/summary-report-development',
              'nf_config': 'config/nextflow',
              'pipeline_version': 'master',
              'parameters':
                  {'hello': 'RUNFOLDER_REPLACE'}}

    cmd_generator = NextflowCommandGenerator(config)
    result = cmd_generator.command('/path/to/runfolder')
    assert result == ['nextflow', '-config', 'config/nextflow', 'run',
                      'Molmed/summary-report-development', '-latest', '-r', 'master', '--hello', '/path/to/runfolder']


def test_raises_on_config_problem():

    config = {'repo': 'Molmed/summary-report-development',
              'nf_config': 'config/nextflow',
              'pipeline_version': 'config/nextflow',
              'parameters':
                  {'hello': 'REPLACE_ERROR'}}
    with pytest.raises(NextflowConfigError):
        NextflowCommandGenerator(config)


def test_raises_on_no_replace_value():
    config = {'repo': 'Molmed/summary-report-development',
              'nf_config': 'config/nextflow',
              'pipeline_version': 'config/nextflow',
              'parameters':
                  {'hello': 'somevalue'}}
    with pytest.raises(NextflowConfigError):
        cmd_generator = NextflowCommandGenerator(config)
