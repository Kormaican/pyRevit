"""Manage pyRevit labs tasks"""
# pylint: disable=invalid-name,broad-except
import sys
import os.path as op
import logging
from typing import Dict

# dev scripts
from scripts import utils
from scripts import configs


logger = logging.getLogger()


def _abort(message):
    print("Build failed")
    print(message)
    sys.exit(1)


def _build(name: str, sln: str, config: str):
    # clean
    slnpath = op.abspath(sln)
    logger.debug("building %s solution: %s", name, slnpath)
    # clean, restore, build
    print(f"Building {name}...")
    report = utils.system(
        [
            "msbuild",
            slnpath,
            "-t:Clean;Restore;Build",
            f"-p:Configuration={config}",
        ]
    )
    passed, report = utils.parse_msbuild_output(report)
    if not passed:
        _abort(report)
    else:
        print(f"Building {name} completed successfully")


def build_engines(_: Dict[str, str]):
    """Build pyRevit engines"""
    _build("ironpython 2.7.* engines", configs.LOADERS, "Release")
    _build("cpython 3.7 engine", configs.CPYTHONRUNTIME, "ReleasePY37")
    _build("cpython 3.8 engine", configs.CPYTHONRUNTIME, "ReleasePY38")


def build_labs(_: Dict[str, str]):
    """Build pyRevit labs"""
    _build("cli and labs", configs.LABS, "Release")


def build_all(_: Dict[str, str]):
    """Build all projects under pyRevit dev"""
    build_labs(_)
    build_engines(_)


def build_telemetry(_: Dict[str, str]):
    """Build pyRevit telemetry server"""
    # get telemetry dependencies
    # configure git globally for `go get`
    utils.system(
        [
            "git",
            "config",
            "--global",
            "http.https://pkg.re.followRedirects",
            "true",
        ]
    )

    print("Updating telemetry server dependencies...")
    report = utils.system(
        ["go", "get", "-d", r".\..."],
        cwd=op.abspath(configs.TELEMETRYSERVERPATH),
    )
    if report:
        print(report)
    print("Telemetry server dependencies successfully updated")

    print("Building telemetry server...")
    report = utils.system(
        [
            "go",
            "build",
            "-o",
            op.abspath(configs.TELEMETRYSERVERBIN),
            op.abspath(configs.TELEMETRYSERVER),
        ],
        cwd=op.abspath(configs.TELEMETRYSERVERPATH),
    )
    print("Building telemetry server succompleted successfully")
