#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['arteria', 'sqlalchemy', 'alembic']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Johan Dahlberg",
    author_email='johan.dahlberg@medsci.uu.se',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Service producing and displaying sequencing reports.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='sequencing_report_service',
    name='sequencing_report_service',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.snpseq.medsci.uu.se/shared/sequencing-report-service/sequencing_report_service',
    version='0.1.0',
    zip_safe=False,
    entry_points={
        'console_scripts': ['sequencing-report-service = sequencing_report_service.app:start']
    },

)
