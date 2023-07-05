import os
import subprocess
from collections.abc import Callable, Iterable

from .entry import Entry, dump_entry, dump_all_entries

QueryFunc = Callable[[str], Iterable[Entry]]


def page_text(text: str) -> None:
    pager = os.getenv("PAGER")
    if pager:
        subprocess.run([pager], input=text, text=True)
    else:
        raise EnvironmentError("Cannot find $PAGER, is this env var set?")


def print_query(
    query_func: QueryFunc,
    query: str,
    print_all: bool=False,
    page: bool=False,
) -> None:
    results = query_func(query)
    if print_all:
        text = dump_all_entries(results)
    else:
        try:
            result = next(iter(results))
        except StopIteration:
            text = ""
        else:
            text = dump_entry(result, 1)
    if page:
        page_text(text)
    else:
        print(text)
