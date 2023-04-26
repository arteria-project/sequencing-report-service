from setuptools import setup, find_packages
from sequencing_report_service import __version__
import os

def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

try:
    with open("requirements/prod", "r") as f:
        install_requires = [x.strip() for x in f.readlines()]
except IOError:
    install_requires = []

setup(
    name='sequencing_report_service',
    version=__version__,
    description="Service producing and displaying sequencing reports.",
    long_description=read_file('README.md'),
    keywords='bioinformatics',
    author='SNP&SEQ Technology Platform, Uppsala University',
    packages=find_packages(include=["sequencing_report_service*"]),
    include_package_data=True,
    entry_points={
        'console_scripts': ['sequencing-report-service = sequencing_report_service.app:start']
    },
    install_requires=install_requires,
)
