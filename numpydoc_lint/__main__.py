"""Main script for numpydoc_lint."""
import argparse
import dataclasses
import importlib
import inspect
import pkgutil
import re
import sys
from enum import EnumMeta
from functools import partial
from pathlib import Path

from loguru import logger
from numpydoc.validate import validate

from numpydoc_lint import NumpydocReturn


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
    for submember_name, submember in inspect.getmembers(
        cls, predicate=partial(_defined_in_class, cls=cls)
    ):
        yield submember_name, submember
        if inspect.isclass(submember):
            yield _class_submembers_r(submember)


def _validate_name(name, args, is_enum):
    validate_results = validate(name)
    validate_results["errors"] = [
        (err_id, err_desc)
        for err_id, err_desc in validate_results["errors"]
        if err_id not in args.exclude_codes
    ]
    if is_enum:
        i, (_, pr01_err) = next(
            (i, x) for i, x in enumerate(validate_results["errors"]) if x[0] == "PR01"
        )
        # numpydoc.validate always finds these vars even if they don't "exist",
        # since they are put in by the EnumMeta Metaclass in a surprising way
        enum_mystery_vars = ["start", "value", "names", "qualname", "module", "type"]
        for var in enum_mystery_vars:
            pr01_err = re.sub(f"'{var}'(, )?", "", pr01_err)
        if "{}" in pr01_err:
            # there are no remaining undocumented variables, remove this error
            del validate_results["errors"][i]
        else:
            # there are still variables that need documenting...
            validate_results["errors"][i] = ("PR01", pr01_err)

    return NumpydocReturn(name=name, **validate_results)


def _all_results(args):
    results = []
    for package_dir in args.packages:
        for _, modname, _ in pkgutil.walk_packages(
            [package_dir], prefix=Path(package_dir).name + "."
        ):
            logger.info(f"Found module: {modname}.")
            if modname in args.exclude_modules:
                continue
            logger.info(f"Attempting to import module: {modname}.")
            mod = importlib.import_module(modname)
            logger.info(f"Import successful: {modname}.")
            for member_name, member in inspect.getmembers(
                mod, lambda mem: inspect.getmodule(mem) == mod
            ):
                full_name = f"{modname}.{member_name}"
                logger.info(f"Found module member: {full_name}.")
                if full_name in args.exclude_members:
                    continue
                if dataclasses.is_dataclass(member) and args.ignore_dataclasses:
                    continue
                results.append(
                    _validate_name(full_name, args, is_enum=type(member) is EnumMeta)
                )
                if inspect.isclass(member):
                    logger.info(f"Recursively traversing class: {full_name}.")
                    for submember_name, _ in _class_submembers_r(member):
                        if submember_name in args.exclude_members:
                            continue
                        full_name = f"{modname}.{member_name}.{submember_name}"
                        logger.info(f"Found class member: {full_name}.")
                        results.append(_validate_name(full_name, args, is_enum=False))
    return results


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Check docstrings for compliance with numpydoc style."
    )
    parser.add_argument(
        "--packages",
        type=str,
        default=[],
        metavar="mod",
        nargs="+",
        help="package directory to recursive search for docstrings",
    )
    parser.add_argument(
        "--exclude-members",
        type=str,
        metavar="func",
        nargs="+",
        default=list(),
        help="functions to exclude from linting",
    )
    parser.add_argument(
        "--exclude-modules",
        type=str,
        metavar="mod",
        nargs="+",
        default=list(),
        help="modules to exclude from linting",
    )
    parser.add_argument(
        "--exclude-codes",
        type=str,
        metavar="errcode",
        nargs="+",
        default=list(),
        help="numpydoc error codes to ignore",
    )
    parser.add_argument(
        "--ignore-dataclasses",
        type=bool,
        default=False,
        help="set to True if you document your dataclass fields 'inline' with Sphinx.",
    )
    return parser.parse_args()


def main():
    """Run command-line application."""
    args = _parse_args()
    results = _all_results(args)
    no_errors = True
    for result in results:
        if result.errors:
            no_errors = False
        print(result)
    if no_errors:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
