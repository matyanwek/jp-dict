import readline
from pathlib import Path
from typing import Optional
from collections.abc import Callable, Iterable, Sequence

from .entry import Entry, dump_entry, dump_all_entries
from .print_ui import page_text

PROMPT = "jp> "
HELP_MESSAGE = r"""
Japanese-to-English Dictionary REPL. To exit, enter CTRL-D or `\exit`.
Enter your query as-is, (e.g. `hello` or `konnichiwa` or `magical girl`) or
enter a command with arguments. Commands start with a '\' and are followed by
args, e.g. `\echo arg1 arg2 arg3`.
Available commands:
    h:
        print this help statement
    exit:
        exits the REPL
    n:
        print the next result
    p:
        print the previous result
    a:
        page all results
    b (args):
        make a query with the backup query function; if args are present, make
        the query with those args, otherwise make the query with the previous
        query args
""".strip()

QueryFunc = Callable[[str], Sequence[Entry]]


class ReplError(Exception):
    pass


def read_history_file(history_file: Path) -> None:
    try:
        readline.read_history_file(history_file)
    except FileNotFoundError:
        pass


def parse_input_str(input_str: str) -> tuple[str, list[str]]:
    if input_str.startswith("\\"):
        command, *args = input_str.lower().lstrip("\\").split()
        return command, args
    else:
        return "", input_str.lower().split()


class Repl:

    def __init__(
        self,
        query_func: QueryFunc,
        backup_query_func: Optional[QueryFunc]=None,
        history_file: Optional[Path]=None,
    ) -> None:
        self.query_func = query_func
        self.backup_query_func = backup_query_func
        self.query = ""
        self.results: Sequence[Entry] = []
        self.result_idx = 0
        if history_file:
            read_history_file(history_file)

    def dump_cur_result(self) -> str:
        return dump_entry(self.results[self.result_idx], self.result_idx + 1)

    def increment_result(self) -> None:
        max_idx = len(self.results) - 1
        if self.result_idx >= max_idx:
            self.result_idx = max_idx
            raise ReplError("No next result")
        else:
            self.result_idx += 1

    def decriment_result(self) -> None:
        min_idx = 0
        if self.result_idx <= min_idx:
            self.result_idx = min_idx
            raise ReplError("No previous result")
        else:
            self.result_idx -= 1

    def search_query(self, args: Iterable[str], backup: bool=False) -> None:
        if args:
            self.query = " ".join(args)
        if not backup:
            self.results = self.query_func(self.query)
        elif self.backup_query_func:
            self.results = self.backup_query_func(self.query)
        else:
            raise ReplError("No backup function defined")
        self.result_idx = 0


def run_once(repl: Repl) -> Repl:
    match parse_input_str(input(PROMPT)):
        case "a" | "all" | "page", _:
            page_text(dump_all_entries(repl.results))
        case "n" | "next", _:
            repl.increment_result()
            print(repl.dump_cur_result())
        case "p" | "prev", _:
            repl.decriment_result()
            print(repl.dump_cur_result())
        case "b" | "backup", args:
            repl.search_query(args, backup=True)
            print(repl.dump_cur_result())
        case "", args:
            repl.search_query(args)
            print(repl.dump_cur_result())
        case "h" | "help", _:
            print(HELP_MESSAGE)
        case "exit", _:
            raise EOFError
        case _:
            print(HELP_MESSAGE)
    return repl


def run_repl(
    query_func: QueryFunc,
    backup_query_func: Optional[QueryFunc]=None,
    history_file: Optional[Path]=None
) -> None:
    repl = Repl(query_func, backup_query_func, history_file)
    while True:
        try:
            repl = run_once(repl)
        except (KeyboardInterrupt, EOFError):
            print()
            break
        except Exception as error:
            print(error)
