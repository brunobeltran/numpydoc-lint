from pathlib import Path

from setuptools import find_packages, setup

import versioneer

setup_dir = Path(__file__).parent
long_description = (setup_dir / "README.md").read_text()

setup(
    name="numpydoc_lint",
    packages=find_packages(exclude=["*test*"]),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Run numpydoc.validate on all docstrings in a package.",
    long_decsription=long_description,
    author="Bruno Beltran <brunobeltran0@gmail.com>",
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "numpydoc"
    ],
)
