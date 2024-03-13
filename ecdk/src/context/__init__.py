from pathlib import Path
from typing import Optional
from core.env import (
    RT_LOCAL, RT_ARES, RT_UNKNOWN,
    RuntimeName,
    getmap_env,
    get_runtime_name
)


class Context:
    def __init__(self, strict: bool = True):
        self.runtime: RuntimeName = get_runtime_name()
        self.is_ares: bool = self.runtime == RT_ARES
        self.repo_dir: Optional[Path] = getmap_env('MY_MASTER_REPO', Path)
        self.short_term_cache_dir: Optional[Path] = getmap_env('MY_SCRATCH', Path)
        self.long_term_cache_dir: Optional[Path] = getmap_env('MY_GROUPS_STORAGE', Path)
        self.instance_metadata_file: Optional[Path] = getmap_env('MY_INSTANCE_METADATA_FILE', Path)
        self.instances_root_dir: Optional[Path] = getmap_env('MY_INSTANCES_DIR', Path)

        if strict:
            assert self.runtime != RT_UNKNOWN
            assert self.repo_dir is not None and self.repo_dir.is_dir()
            assert self.short_term_cache_dir is not None and self.short_term_cache_dir.is_dir()
            assert self.long_term_cache_dir is not None and self.long_term_cache_dir.is_dir()
            assert self.instance_metadata_file is not None and self.instance_metadata_file.is_file()
            assert self.instances_root_dir is not None and self.instances_root_dir.is_dir()

