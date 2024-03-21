from typing import Iterable, Optional, TypeVar, Callable
import itertools as it

T = TypeVar('T')
U = TypeVar('U')


def find_first_or_none(iterable: Iterable[T], pred: Callable[[T], bool]) -> Optional[T]:
    for item in iterable:
        if pred(item):
            return item
    return None


# TODO: Type this properly
def iter_batched(iterable: Iterable, n: int):
    assert n >= 1
    iterator = iter(iterable)
    while batch := tuple(it.islice(iterator, n)):
        yield batch


def nonesafe_map(obj: Optional[T], mapping: Callable[[T], U]) -> Optional[U]:
    if obj is None:
        return None
    return mapping(obj)

