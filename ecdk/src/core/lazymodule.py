import importlib as ilib
from typing import Optional


class LazyModule:
    """ Descriptor, aimed to be used inside classes, to load particular modules only when they are used.

        This only looks like instance of module is created for each instance of this class. In reality
        we take advantage of importlib cache: when the module is loaded by different instance of LazyModule
        we receive the same reference thanks to the importlib cache.
    """


    def __init__(self, name: str, package: Optional[str] = None) -> None:
        self._name = name
        self._package = package
        self._instance = None


    def __get__(self, instance, owner=None):
        if self._instance is None:
            self._instance = ilib.import_module(self._name, package=self._package)
            assert self._instance is not None
        return self._instance


    def get(self):
        return self.__get__(None)

