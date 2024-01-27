from typing import Iterable, Optional, TypeVar, Callable
import itertools as it

T = TypeVar('T')


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

