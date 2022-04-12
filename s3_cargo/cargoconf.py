from os import getenv
from pathlib import Path, PurePath
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, validator

__all__ = ("CargoOptions", "ResourceItem", "Future", "CargoConfig")


class CargoOptions(BaseModel):
    projectid: str
    destination: Path = Path(".")
    url: HttpUrl
    bucket: str
    user: str = ""

    cleanup_workdir: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = getenv("USERNAME") or getenv("USER") or "default"


class ResourceItem(BaseModel):
    selector: str
    mode: str = "persistent"
    bind: str = ""
    unpack: bool = False
    unravel: bool = False
    keeparchive: bool = True

    @validator("mode")
    def check_mode(cls, v):
        if v.lower() not in {"persistent", "transient"}:
            raise ValueError(
                f'mode can be either "transient" or "persistent".Got: "{v}"'
            )

        return v


class Future(BaseModel):
    name: str
    compress: str = ""
    selector: List[str]
    emit: List[str]

    @validator("name")
    def validate_name(cls, v):
        return PurePath(v).stem


class CargoConfig(BaseModel):
    options: CargoOptions
    resources: List[ResourceItem] = []
    futures: List[Future] = []

    @validator("resources", each_item=True, pre=True)
    def format_resourceitem_input(cls, v):

        if isinstance(v, str):
            name, settings = v, dict()
        else:
            name, settings = v.popitem()

        return dict(selector=name, **settings)
