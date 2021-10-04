"""Wrapper for running numpydoc.validate on entire packages."""
from dataclasses import dataclass
from typing import List, Tuple

from . import _version

__version__ = _version.get_versions()["version"]


@dataclass
class NumpydocReturn:
    """Dataclass wrapper for return dict from numpydoc.validate."""

    name: str
    type: str
    docstring: str
    deprecated: bool
    file: str
    file_line: int
    errors: List[Tuple[str, str]]
    examples_errors: str = None

    def __str__(self):
        """Display only info relevant to finding error."""
        prefix = f"{self.file}:{self.name}:{self.file_line}:: "
        if self.errors:
            return f"{prefix}{self.errors}"
        else:
            return f"{prefix}No errors!"
