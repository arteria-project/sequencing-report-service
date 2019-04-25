"""
Module containg code relating to commands
"""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class CommandWithEnv:
    """
    Container for a command and the environment it needs to use.
    """
    command: List[str]
    environment: Dict[str, str]
