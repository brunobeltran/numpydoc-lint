"""Main script for numpydoc_lint."""
import argparse
import importlib
import inspect
import pkgutil
from functools import partial
from pathlib import Path

from numpydoc.validate import validate


def _defined_in_class(meth, cls):
    if inspect.ismethod(meth):
        for cls_i in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls_i.__dict__:
                return cls == cls_i
    if inspect.isfunction(meth):
        return cls == getattr(
            inspect.getmodule(meth),
            meth.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0],
            None,
        )


def _class_submembers_r(cls):
    for submember in inspect.getmembers(
        cls, predicate=partial(_defined_in_class, cls=cls)
    ):
        yield submember
        if inspect.isclass(submember):
            yield _class_submembers_r(submember)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check docstrings for compliance with numpydoc style."
    )
    parser.add_argument(
        "--packages",
        type=str,
        metavar="mod",
        nargs="+",
        help="package directory to recursive search for docstrings",
    )
    parser.add_argument(
        "--exclude-members",
        type=str,
        metavar="func",
        nargs="+",
        help="functions to exclude from linting",
    )
    parser.add_argument(
        "--exclude-modules",
        type=str,
        metavar="mod",
        nargs="+",
        help="modules to exclude from linting",
    )
    args = parser.parse_args()
    print(args)

    results = []
    for package_dir in args.packages:
        for _, modname, _ in pkgutil.walk_packages(
            package_dir, prefix=Path(package_dir).name
        ):
            mod = importlib.import_module(modname)
            for member in inspect.getmembers(
                mod, lambda mem: inspect.getmodule(mem) == mod
            ):
                if inspect.isclass(member):
                    for submember in _class_submembers_r(member):
                        results.append(validate(submember))
                else:
                    results.append(validate(member))
    print(results)
