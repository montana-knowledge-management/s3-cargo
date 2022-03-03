import tarfile
from fnmatch import fnmatch
from io import StringIO
from itertools import chain
from json import dumps
from os import lstat
from os.path import expandvars
from pathlib import Path, PurePath
from shutil import rmtree
from zipfile import ZIP_DEFLATED, ZipFile

import boto3
from pydantic import FilePath
from pyunpack import Archive
from yaml import safe_load

from s3_cargo import CargoConfig, fail
from s3_cargo.cargoconf import Future, ResourceItem
from s3_cargo.msgformat import green


class Cargo:
    def __init__(self, cargoconf: FilePath, root: str = ""):
        self.cfgfile = cargoconf
        self.cfg = load_config_file(self.cfgfile)
        if root:
            self.dst = (
                Path(root)
                .joinpath(self.cfg.options.destination)
                .expanduser()
                .resolve()
            )
        else:
            self.dst = cargoconf.parent.joinpath(self.cfg.options.destination)

        self.s3 = boto3.resource("s3", endpoint_url=self.cfg.options.url)
        self.bucket = self.s3.Bucket(self.cfg.options.bucket)

    @classmethod
    def from_json(cls, config: dict, root: str):
        return cls(StringIO(dumps(config)), root=root)

    def open_session(self):
        print("OPEN SESSION")
        projectid = self.cfg.options.projectid
        if self.cfg.options.cleanup_workdir and self.dst.exists():
            rmtree(self.dst)

        self.dst.mkdir(exist_ok=True, parents=True)
        fetched_keys = tuple(
            chain(
                self._fetch_keys(f"{projectid}/input/"),
                self._fetch_keys(f"{projectid}/home/{self.cfg.options.user}/"),
                self._fetch_keys(f"{projectid}/shared/"),
                self._fetch_keys(f"{projectid}/project_results/"),
            )
        )
        for resource in self.cfg.resources:
            filtered_keys = self._fileter_keys(fetched_keys, resource)
            self._pull_keys(resource, filtered_keys)

    def __enter__(self):
        self.open_session()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_session()

    def _fetch_keys(self, prefix):
        try:
            yield from self.bucket.objects.filter(Prefix=prefix)
        except Exception as e:
            print(fail(e))

    def _pull_keys(self, resource, keys):
        for key in keys:
            if key.key[-1] == "/":
                continue

            fname = Path(*key.key.split("/")[1:])
            asfile = self.dst.joinpath(resource.bind)

            if resource.unravel:
                asfile = asfile.joinpath(fname.name)
            else:
                asfile = asfile.joinpath(fname)

            asfile.parent.mkdir(parents=True, exist_ok=True)
            if asfile.exists():
                if resource.mode == "transient":
                    asfile.unlink()
                else:
                    continue

            self._download_key(key, asfile)
            if resource.unpack:
                if asfile.suffix == ".zip":
                    tempzfile = ZipFile(asfile)
                    # TODO: contents of the zip file can be persistent
                    tempzfile.extractall(path=asfile.parent.as_posix())

                elif asfile.suffix == ".bz2":
                    with tarfile.open(asfile, "r:bz2") as z:
                        z.extractall(path=asfile.parent.as_posix())

                elif asfile.suffix == ".rar":
                    Archive(asfile.as_posix()).extractall(
                        asfile.parent.as_posix()
                    )

                if not resource.keeparchive:
                    asfile.unlink()

    def _fileter_keys(self, keys, resource: ResourceItem):
        for key in keys:
            first, *rest = PurePath(resource.selector).parts
            if first == "home":
                selector = PurePath(
                    self.cfg.options.projectid,
                    first,
                    self.cfg.options.user,
                    *rest,
                )
            else:
                selector = PurePath(self.cfg.options.projectid, first, *rest)

            if fnmatch(key.key, selector.as_posix()):
                yield key

    def _download_key(self, key, to: Path):
        print(key.key.rjust(len(key.key) + 10), end="", flush=True)

        def callback(key, ch):
            callback.done += ch
            progress = f"{callback.done/key.size*100:.2f} %".center(10)
            print(f"\r{progress}{key.key}", end="", flush=True)

        callback.done = 0
        self.bucket.download_file(
            key.key, to.as_posix(), Callback=lambda ch: callback(key, ch)
        )
        print("\r" + green("DONE".center(10)) + key.key)

    def close_session(self):
        print("CLOSE SESSION\n")
        for future in self.cfg.futures:
            items = tuple(gather_future_items(self.dst, future))
            if future.compress:
                self._compress_push_future(future, items)
            else:
                self._push_future(future, items)

    def _compress_push_future(self, future, items):
        filename = self.dst / f"{future.name}.{future.compress}"
        if future.compress == "zip":
            with ZipFile(
                filename, "w", compression=ZIP_DEFLATED, compresslevel=9
            ) as zfile:
                for item in items:
                    zfile.write(item, item.name)

            if not zfile.namelist():
                filename.unlink()
                return False

        for dest in future.emit:
            dest = self._validate_future_destination(dest)
            key = "/".join([self.cfg.options.projectid, dest, filename.name])

            self._upload_item(filename, key)

        filename.unlink()

    def _push_future(self, future, items):
        for item in items:
            for dest in future.emit:
                dest = self._validate_future_destination(dest)
                key = "/".join(
                    [self.cfg.options.projectid, dest, future.name, item.name]
                )
                self._upload_item(item, key)

    def _validate_future_destination(self, d):
        first, *rest = PurePath(d).parts
        if first == "shared":
            return PurePath("shared", *rest).as_posix()
        elif first == "project_results":
            return PurePath("project_results", *rest).as_posix()
        elif first == "input":
            return PurePath(
                "home", self.cfg.options.user, "input", *rest
            ).as_posix()
        else:
            return PurePath("home", self.cfg.options.user, *rest).as_posix()

    def _upload_item(self, item, key):
        def callback(key, ch):
            callback.done += ch
            progress = f"{callback.done / callback.size * 100:.2f} %".center(10)
            print(f"\r{progress}{key}", end="", flush=True)

        callback.done = 0
        callback.size = lstat(item).st_size
        self.bucket.upload_file(
            item.as_posix(), key, Callback=lambda ch: callback(key, ch)
        )
        print(green("\r" + "DONE".center(10)) + key)


def load_config_file(config_file: FilePath) -> CargoConfig:
    try:
        content = config_file.read_text()
    except AttributeError:
        content = config_file.read()

    cfg_raw = safe_load(expandvars(content))
    cfg = CargoConfig(**cfg_raw)
    # pprint(loads(cfg.json()))
    return cfg


def gather_future_items(base: Path, future: Future):
    for selector in future.selector:
        yield from base.glob(selector)
