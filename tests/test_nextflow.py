
import pytest
import datetime
import tempfile
import pathlib
import yaml
import shutil

from sequencing_report_service.nextflow import NextflowCommandGenerator, NextflowConfigError


def test_command():
    config = {
        'main_workflow_path': 'Molmed/summary-report-development',
        'nextflow_parameters': {
            'config': 'config/nextflow',
            'profile': 'singularity,snpseq',
        },
        'environment': {
            'NXF_TEMP': '/tmp_foo',
            'TEST_RUNFOLDER': '{runfolder_name}',
            'TEST_PATH': '{runfolder_path}',
            'TEST_YEAR': '{current_year}',
        },
        'pipeline_parameters': {
            'hello': '{runfolder_path}',
            'year': '{current_year}',
            'name': '{runfolder_name}',
        }
    }

    with tempfile.TemporaryDirectory() as pipeline_config_dir:
        with open(
                pathlib.Path(pipeline_config_dir) / "seqreports.yml",
                'w') as config_file:
            config_file.write(yaml.dump(config))
        with open(
                pathlib.Path(pipeline_config_dir) / "pipeline.yml",
                'w') as config_file:
            config_file.write(yaml.dump(config))
        shutil.copyfile(
            "config/pipeline_config/schema.json",
            pathlib.Path(pipeline_config_dir) / "schema.json"
        )

        cmd_generator = NextflowCommandGenerator(pipeline_config_dir)
        results = [
            cmd_generator.command('/path/to/runfolder'),
            cmd_generator.command('/path/to/runfolder', "pipeline"),
        ]

        for result in results:
            assert result['command'] == [
                'nextflow',
                'run', 'Molmed/summary-report-development',
                '-config', 'config/nextflow',
                '-profile', 'singularity,snpseq',
                '--hello', '/path/to/runfolder',
                '--name', 'runfolder',
                '--year', str(datetime.datetime.now().year),
            ]

            assert result['environment'] == {
                'NXF_TEMP': '/tmp_foo',
                'TEST_RUNFOLDER': 'runfolder',
                'TEST_PATH': '/path/to/runfolder',
                'TEST_YEAR': str(datetime.datetime.now().year),
            }


def test_raises_config_file_not_found():
    with tempfile.TemporaryDirectory() as pipeline_config_dir:
        cmd_generator = NextflowCommandGenerator(pipeline_config_dir)
        with pytest.raises(FileNotFoundError):
            cmd_generator.command('/path/to/runfolder')
