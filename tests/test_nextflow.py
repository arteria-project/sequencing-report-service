
import pytest
import datetime

from sequencing_report_service.nextflow import NextflowCommandGenerator, NextflowConfigError


def test_command():
    config = {'main_workflow_path': 'Molmed/summary-report-development',
              'nf_config': 'config/nextflow',
              'nf_profile': 'singularity,snpseq',
              'environment':
              {
                  'NXF_TEMP': '/tmp_foo',
                  'TEST_RUNFOLDER': '${DEFAULT:runfolder_name}',
                  'TEST_PATH': '${DEFAULT:runfolder_path}',
                  'TEST_YEAR': '${DEFAULT:current_year}',
              },
              'parameters':
                  {'hello': '${DEFAULT:runfolder_path}',
                   'year': '${DEFAULT:current_year}',
                   'name': '${DEFAULT:runfolder_name}'}}

    cmd_generator = NextflowCommandGenerator(config)
    result = cmd_generator.command('/path/to/runfolder')
    assert result['command'] == [
        'nextflow',
        '-config', 'config/nextflow',
        'run', 'Molmed/summary-report-development',
        '-profile', 'singularity,snpseq',
        '--hello', '/path/to/runfolder',
        '--year', str(datetime.datetime.now().year),
        '--name', 'runfolder',
    ]

    assert result['environment'] == {
        'NXF_TEMP': '/tmp_foo',
        'TEST_RUNFOLDER': 'runfolder',
        'TEST_PATH': '/path/to/runfolder',
        'TEST_YEAR': str(datetime.datetime.now().year),
    }


def test_raises_on_no_parameters_section():

    config = {'main_workflow_path': 'Molmed/summary-report-development',
              'nf_config': 'config/nextflow'}
    with pytest.raises(NextflowConfigError):
        NextflowCommandGenerator(config)


def test_raises_on_no_parameters_main_workflow_path():

    config = {'nf_config': 'config/nextflow',
              'parameters':
              {'hello': '${DEFAULT:runfolder_path}'}}
    with pytest.raises(NextflowConfigError):
        NextflowCommandGenerator(config)
