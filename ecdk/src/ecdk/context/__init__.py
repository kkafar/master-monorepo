import tomllib
from pathlib import Path
from typing import Optional
from core.env import (
    RT_LOCAL, RT_ARES, RT_UNKNOWN,
    RuntimeName,
    getmap_env,
    get_runtime_name
)
from core.version import Version
from core.fs import get_data_dir_from_ecdk_dir, get_raw_solutions_dir_from_data_dir


class Context:
    def __init__(self, strict: bool = True):
        """ :param strict: whether to run assertions """

        self.runtime: RuntimeName = get_runtime_name()
        self.is_ares: bool = self.runtime == RT_ARES
        self.repo_dir: Optional[Path] = getmap_env('MY_MASTER_REPO', Path)
        self.ecdk_dir: Optional[Path] = getmap_env('MY_ECDK', Path)
        self.short_term_cache_dir: Optional[Path] = getmap_env('MY_SCRATCH', Path)
        self.long_term_cache_dir: Optional[Path] = getmap_env('MY_GROUPS_STORAGE', Path)
        self.instance_metadata_file: Optional[Path] = getmap_env('MY_INSTANCE_METADATA_FILE', Path)
        self.instances_root_dir: Optional[Path] = getmap_env('MY_INSTANCES_DIR', Path)
        self.ecdk_version: Version = self._resolve_ecdk_version()

        if strict:
            assert self.runtime != RT_UNKNOWN
            assert self.repo_dir is not None and self.repo_dir.is_dir()
            assert self.ecdk_dir is not None and self.repo_dir.is_dir()
            assert self.short_term_cache_dir is not None and self.short_term_cache_dir.is_dir()
            assert self.long_term_cache_dir is not None and self.long_term_cache_dir.is_dir()
            assert self.instance_metadata_file is not None and self.instance_metadata_file.is_file()
            assert self.instances_root_dir is not None and self.instances_root_dir.is_dir()
            assert self.ecdk_version is not None and isinstance(self.ecdk_version, Version)

    def ecdk_input_data_dir(self) -> Path:
        return get_data_dir_from_ecdk_dir(self.ecdk_dir)

    def ecdk_db_path(self) -> Path:
        return get_data_dir_from_ecdk_dir(self.ecdk_dir).joinpath('main.db')

    def ecdk_instance_solutions_dir(self) -> Path:
        return get_raw_solutions_dir_from_data_dir(self.ecdk_input_data_dir())

    def _resolve_ecdk_version(self) -> Version:
        with open("pyproject.toml", "rb") as file:
            pyproject_file = tomllib.load(file)
            version = pyproject_file.get('project', {}).get('version')
            return Version.from_str(version)


_CONTEXT: Optional[Context] = None


def initialize_context(strict: bool = True) -> Context:
    global _CONTEXT
    if _CONTEXT is None:
        _CONTEXT = Context(strict=strict)
    return _CONTEXT


def get_context() -> Context:
    global _CONTEXT
    if _CONTEXT is None:
        raise RuntimeError("Context has not been initialised yet")
    return _CONTEXT



