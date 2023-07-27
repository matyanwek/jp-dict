import os
import subprocess
from collections.abc import Callable, Sequence

from .entry import Entry, dump_entry, dump_all_entries

QueryFunc = Callable[[str], Sequence[Entry]]


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
    if not results:
        print(f"No results for {query}")
        return
    elif print_all:
        text = dump_all_entries(results)
    else:
        text = dump_entry(results[0], 1)
    if page:
        page_text(text)
    else:
        print(text)
