from pathlib import Path

from setuptools import setup

import versioneer

setup_dir = Path(__file__).parent
long_description = (setup_dir / "README.md").read_text()

setup(
    name="numpydoc_lint",
    packages=["numpydoc_lint"],
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Run numpydoc.validate on all docstrings in a package.",
    long_decsription=long_description,
    author="Bruno Beltran <brunobeltran0@gmail.com>",
    entry_points={"console_scripts": ["numpydoc_lint=numpydoc_lint.__main__:main"]},
    python_requires=">=3.7",
    install_requires=["numpydoc"],
)
