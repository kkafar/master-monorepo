from typing import Iterable, Optional, TypeVar, Callable
from pathlib import Path
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


def write_string_to_file(string: str, file: Path, append: bool = False):
    # https://stackoverflow.com/questions/30686701/python-get-size-of-string-in-bytes
    string_byte_count = len(string.encode('utf-8'))
    open_mode = 'w+' if append else 'w'

    writed_bytes_count = 0
    with open(file, mode=open_mode, encoding='utf-8') as writer:
        writed_bytes_count = writer.write(string)

    assert string_byte_count == writed_bytes_count

