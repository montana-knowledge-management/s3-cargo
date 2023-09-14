from os import getenv
from pathlib import Path, PurePath
from typing import Annotated, List

from pydantic import BaseModel, BeforeValidator, HttpUrl, field_validator, validator

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

    @field_validator("mode")
    @classmethod
    def check_mode(cls, v):
        if v.lower() not in {"persistent", "transient"}:
            raise ValueError(f'mode can be either "transient" or "persistent".Got: "{v}"')

        return v


class Future(BaseModel):
    name: str
    compress: str = ""
    selector: List[str]
    emit: List[str]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return PurePath(v).stem


def format_resourceitem_input(v):
    items = []
    for vi in v:
        if isinstance(vi, str):
            name, settings = vi, dict()
        else:
            name, settings = vi.popitem()

        items.append(dict(selector=name, **settings))
    return items


class CargoConfig(BaseModel):
    options: CargoOptions
    resources: Annotated[List[ResourceItem], BeforeValidator(format_resourceitem_input)] = []
    futures: List[Future] = []
