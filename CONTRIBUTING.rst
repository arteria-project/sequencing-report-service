.. highlight:: shell

============
Contributing
============

Get Started!
------------

Ready to contribute? Here's how to set up `sequencing_report_service` for local development.

1. Clone the project repo::

    $ git clone git@gitlab.snpseq.medsci.uu.se:shared/sequencing-report-service.git

3. Install your local copy into a virtualenv. Create a virtual environment with Conda and install the project there::

    $ conda create -n sequencing_report_service python=3.6
    $ source activate sequencing_report_service
    $ python setup.py develop

4. Create a branch for local development (if these are attached to a Jira ticket include the ticket number in
   branch name::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ flake8 sequencing_report_service tests
    $ python setup.py test or py.test
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Create a merge request on Gitlab in the UI.

Pull Request Guidelines
-----------------------

Before you submit a merge request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.

Tips
----

To run a subset of tests::

$ py.test tests.test_sequencing_report_service


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

$ bumpversion patch # possible: major / minor / patch
$ git push
$ git push --tags

TODO Add docs on continuous deployment here.

