from s3cargo.msgformat import *


def test_green():
    assert green("test") == "\033[92mtest\033[0m"


def test_red():
    assert red("test") == "\033[91mtest\033[0m"


def test_warning():
    assert warning("test") == f"\033[93mtest\033[0m"


def test_bold():
    assert bold("test") == f"\033[1mtest\033[0m"


def test_underline():
    assert underline("test") == f"\033[4mtest\033[0m"


def test_success():
    assert success("test") == "\033[92m\033[1mtest\033[0m\033[0m"


def test_fail():
    assert fail("test") == "\033[91m\033[1mtest\033[0m\033[0m"
