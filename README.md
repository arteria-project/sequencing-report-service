Sequencing Report Service
=========================

Service used to start nextflow pipelines with passed config variables 

Current nextflow pipelines that can be started by 
--------

* [nf-core/demultiplex](https://nf-co.re/demultiplex/)
* [nf-core/sarek](https://nf-co.re/sarek/)


Local Development
----------------

#### Dependency management with UV

We use UV for fast and reliable Python dependency management. To get started:

1. Install UV:
```bash
pip install uv
```

2. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies: (Use '--dev' for dev group )
```bash
uv sync --all-groups  # Install all project dependencies from the lockfile
```

```bash
uv add <'package'>  # Add dependencies to the project and added to the project's pyproject.toml file.
```

```bash
uv remove <'package'>  # Removes dependencies in the project and removes in the project's pyproject.toml file.
```

#### Dependency Locking

We use UV's lockfile functionality to ensure reproducible builds:
NOTE: `uv add` and `uv remove` usually edit both pyproject.toml and uv.lock but 
one can run the command below if you delete the lock file to regenerate

1. Generate/update lockfile:
```bash
uv lock
```
