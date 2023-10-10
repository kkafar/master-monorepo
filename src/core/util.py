from typing import Iterable, Optional, TypeVar, Callable

T = TypeVar('T')


def find_first_or_none(iterable: Iterable[T], pred: Callable[[T], bool]) -> Optional[T]:
    for item in iterable:
        if pred(item):
            return item
    return None


