from attr import assoc
import pytest
import os
from s3cargo.cargomain import Cargo
from test.utils import URL, BUCKETNAME, TESTROOT, export_config
from shutil import rmtree


@pytest.fixture
def starting_config():
    cfg = {
        "options": {
            "projectid": "test_project",
            "destination": "test_workdir",
            "url": URL,
            "bucket": BUCKETNAME,
        },
        "resources": [{'input/*.txt':{'mode':'transient', 'unravel':True }}],
        "futures": [],
    }
    yield cfg

    try:
        # rmtree(TESTROOT.joinpath(cfg["options"]["destination"]))
        # TESTROOT.joinpath("cargoconf.yml").unlink()
        pass
    except FileNotFoundError:
        pass


def test_session(starting_config):
    cfg = export_config(starting_config)
    with Cargo(cfg) as c:
        c.cfg.options.user = 'testuser'
        num_files = sum(fi.is_file() for fi in c.dst.glob('*'))
        assert num_files == 11
