from test.utils import (
    BUCKETNAME,
    PROJECTID,
    RESULTS,
    TESTROOT,
    URL,
    cleanup_bucket_folder,
    is_key_exists,
)

import pytest
import yaml

from s3_cargo import Cargo


@pytest.fixture
def starting_config():
    cleanup_bucket_folder(RESULTS)
    cleanup_bucket_folder("home")
    cfg = {
        "options": {
            "projectid": PROJECTID,
            "destination": "resources/close_session",
            "url": URL,
            "bucket": BUCKETNAME,
        },
        "resources": [],
        "futures": [],
    }
    yield cfg

    TESTROOT.joinpath("cargoconf.yml").unlink()


def export_config(cfg):
    """
    Export the config dictionary into the cargoconf.yml file.
    """
    f = TESTROOT.joinpath("cargoconf.yml")
    f.write_text(yaml.dump(cfg))
    return f


def test_upload_file(starting_config):
    """
    Upload 1 file into the project_results folder.
    """
    starting_config["futures"] = [
        {
            "name": "folder_1",
            "selector": ["testfile1.txt"],
            "emit": ["home", "shared", RESULTS, "input"],
        }
    ]
    c = Cargo(export_config(starting_config))
    c.cfg.options.user = "testuser"
    c.close_session()
    assert is_key_exists(f"{PROJECTID}/{RESULTS}/folder_1/testfile1.txt")
    assert is_key_exists(f"{PROJECTID}/home/testuser/folder_1/testfile1.txt")
    assert is_key_exists(f"{PROJECTID}/shared/folder_1/testfile1.txt")
    assert not is_key_exists(f"{PROJECTID}/input/folder_1/testfile1.txt")


def test_zip_upload_file(starting_config):
    """
    Zip 1 file then upload to multiple places.
    """
    starting_config["futures"] = [
        {
            "name": "compress_test",
            "compress": "zip",
            "selector": ["testfile1.txt"],
            "emit": ["home", "shared", RESULTS, "input"],
        }
    ]
    c = Cargo(export_config(starting_config))
    c.cfg.options.user = "testuser"
    c.close_session()
    assert is_key_exists(f"{PROJECTID}/{RESULTS}/compress_test.zip")
    assert is_key_exists(f"{PROJECTID}/home/testuser/compress_test.zip")
    assert is_key_exists(f"{PROJECTID}/shared/compress_test.zip")
    assert not is_key_exists(f"{PROJECTID}/input/compress_test.zip")


# def test_bz2_upload_file(starting_config):
#     """
#     Archive 1 file into tar.bz2 format then upload to multiple places.
#     """
#     starting_config['futures'] = [
#         {'name': 'compress_test',
#          'compress': 'bz2',
#          'selector': ['testfile1.txt'],
#          'emit': ['home', 'shared', RESULTS, 'input']}
#     ]
#     c = Cargo(export_config(starting_config))
#     c.cfg.options.user = 'testuser'
#     c.close_session()
#     assert is_key_exists(f'{PROJECTID}/{RESULTS}/compress_test.tar.bz2')
#     assert is_key_exists(f'{PROJECTID}/home/testuser/compress_test.tar.bz2')
#     assert is_key_exists(f'{PROJECTID}/shared/compress_test.tar.bz2')
#     assert not is_key_exists(f'{PROJECTID}/input/compress_test.tar.bz2')
