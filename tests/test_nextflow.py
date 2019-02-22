
import pytest

from sequencing_report_service.nextflow import NextflowCommandGenerator, NextflowConfigError

def test_command():
    config = {'cmd': 'echo',
              'parameters':
                  {'hello': 'RUNFOLDER_REPLACE'}}

    cmd_generator = NextflowCommandGenerator(config)
    result = cmd_generator.command('/path/to/runfolder')
    assert result == ['echo', '--hello', '/path/to/runfolder']


def test_raises_on_config_problem():

    config = {'parameters':
                {'hello': 'RUNFOLDER_REPLACE'}}
    with pytest.raises(NextflowConfigError):
        NextflowCommandGenerator(config)

def test_raises_on_no_replace_value():
    config = {'cmd': 'echo',
              'parameters':
                  {'hello': 'somevalue'}}
    with pytest.raises(NextflowConfigError):
        cmd_generator = NextflowCommandGenerator(config)