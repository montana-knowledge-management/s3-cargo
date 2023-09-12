from shutil import rmtree
from test.utils import BUCKETNAME, TESTROOT, URL, export_config

import pytest

from s3_cargo import Cargo
from s3_cargo.cargomain import load_config_file


@pytest.fixture
def starting_config():
    cfg = {
        "options": {
            "projectid": "test_project",
            "destination": "test_workdir",
            "url": URL,
            "bucket": BUCKETNAME,
        },
        "resources": [],
        "futures": [],
    }
    yield cfg

    try:
        rmtree(TESTROOT.joinpath(cfg["options"]["destination"]))
        TESTROOT.joinpath("cargoconf.yml").unlink()
    except FileNotFoundError:
        pass


def test_invalid_file_mode(starting_config):
    """
    Pydantic should raise an exception if the file mode is not `transient` or
    `persistent`.
    """
    file = "input/f-80e1.txt"
    starting_config["resources"] = [{f"file": {"mode": "invalid_mode"}}]
    with pytest.raises(ValueError):
        load_config_file(export_config(starting_config))


def test_1_file_root(starting_config):
    """
    Select 1 file from input/ root and place it under the local root, test_workdir/
    Expected result should be: test_workdir/f-80e1.txt
    """
    file = "input/f-80e1.txt"
    starting_config["resources"] = [{file: {"mode": "transient"}}]
    test_cfg = export_config(starting_config)
    c = Cargo(test_cfg)
    c.open_session()
    assert c.dst.joinpath(file).exists()


def test_1_file_root_bind(starting_config):
    """
    Select 1 file from input/ root and place it under a specified subdirectory.
    """
    file = "input/f-80e1.txt"
    starting_config["resources"] = [{file: {"bind": "nested1/nested2"}}]
    test_cfg = export_config(starting_config)
    c = Cargo(test_cfg)
    c.open_session()
    assert c.dst.joinpath("nested1/nested2", file).exists()


def test_1_file_nested_no_bind_no_unravel(starting_config):
    """
    Select a nested file from input/ and place it under the local root directory.
    """
    file = "input/lowercased/nested_1/nested_12/f-77fd.txt"
    starting_config["resources"] = [file]
    test_cfg = export_config(starting_config)
    c = Cargo(test_cfg)
    c.open_session()
    assert c.dst.joinpath(file).exists()


def test_1_file_nested_bind_no_unravel(starting_config):
    """
    Select a nested file from input/ and place it under the specified directory.
    """
    file = "input/lowercased/nested_1/nested_12/f-77fd.txt"
    bind = "bind1/bind2"
    starting_config["resources"] = [{file: {"bind": bind}}]
    test_cfg = export_config(starting_config)
    c = Cargo(test_cfg)
    c.open_session()
    assert c.dst.joinpath(bind, file).exists()


def test_1_file_nested_no_bind_unravel(starting_config):
    """
    Select a nested file from input/ and place it under the local root directory without the nesting.
    """
    file = "input/lowercased/nested_1/nested_12/f-77fd.txt"
    starting_config["resources"] = [{file: {"unravel": True}}]
    test_cfg = export_config(starting_config)
    c = Cargo(test_cfg)
    c.open_session()
    assert c.dst.joinpath("f-77fd.txt").exists()


def test_1_file_nested_bind_unravel(starting_config):
    """
    Select a nested file from input/ and place it under the specified directory without the nesting.
    """
    file = "input/lowercased/nested_1/nested_12/f-77fd.txt"
    bind = "bind1/bind2"
    starting_config["resources"] = [{file: {"bind": bind, "unravel": True}}]
    test_cfg = export_config(starting_config)
    c = Cargo(test_cfg)
    c.open_session()
    assert c.dst.joinpath(bind, "f-77fd.txt").exists()


def test_zipped_no_unpack(starting_config):
    """
    Select a zipped file from input/ and place it under the local root directory.
    """
    file = "input/f13.zip"
    starting_config["resources"] = [file]
    test_cfg = export_config(starting_config)
    c = Cargo(test_cfg)
    c.open_session()
    assert c.dst.joinpath(file).exists()


def test_zipped_unpack(starting_config):
    """
    Select a zipped file from input/ and place it under the local root directory then unpack it.
    """
    starting_config["resources"] = [
        {"input/f13.zip": {"unpack": True, "keeparchive": False}},
        {"input/f36.tar.bz2": {"unpack": True, "keeparchive": False}},
    ]
    test_cfg = export_config(starting_config)
    c = Cargo(test_cfg)
    c.open_session()
    assert c.dst.joinpath("input", "f-77fd.txt").exists()
    assert c.dst.joinpath("input", "f-80e1.txt").exists()
    assert c.dst.joinpath("input", "f-84f5.txt").exists()
    assert not c.dst.joinpath("input", "f13.zip").exists()

    assert c.dst.joinpath("input", "f-42b8.txt").exists()
    assert c.dst.joinpath("input", "f-5a4c.txt").exists()
    assert c.dst.joinpath("input", "f-68eb.txt").exists()
    assert not c.dst.joinpath("input", "f36.tar.bz2").exists()


def test_non_existing_file(starting_config):
    file = "input/invalid_file"
    starting_config["resources"] = [file]
    test_cfg = export_config(starting_config)
    c = Cargo(test_cfg)
    c.open_session()
    assert not c.dst.joinpath(file).exists()
