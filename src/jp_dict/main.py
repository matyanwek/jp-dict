import sys
import functools
from pathlib import Path
from argparse import ArgumentParser
from collections.abc import Callable, Sequence

from .ui import print_query, run_repl
from .dict_query import update_dictionary, search_dictionary, clean_dictionary

APP_DESCRIPTION = """
Search for terms and return a listing of Japanese-to-English dictionary results.
Search terms can bee in English or Japanese. Without arguments, opens and
interactive REPL for searching terms.
""".strip()


def parse_args(args: Sequence[str]) -> Callable[[], None]:
    parser = ArgumentParser(
        description=APP_DESCRIPTION,
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="update the dictionary data and exit; overrides other arguments",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="delete all dictionary files",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="when used with a search term, prints all results to stdout",
    )
    parser.add_argument(
        "--hist",
        type=Path,
        const=None,
        help="location of the readline history file for use in REPL",
    )
    parser.add_argument(
        "search_strs",
        nargs="*",
    )
    parsed_args = parser.parse_args(args)
    if parsed_args.update:
        return update_dictionary
    elif parsed_args.clean:
        return clean_dictionary
    elif parsed_args.search_strs:
        return functools.partial(
            print_query,
            query=" ".join(parsed_args.search_strs),
            query_func=search_dictionary,
            print_all=parsed_args.all,
        )
    else:
        return functools.partial(
            run_repl,
            query_func=search_dictionary,
            history_file=parsed_args.hist,
        )


def main() -> None:
    func = parse_args(sys.argv[1:])
    func()


if __name__ == "__main__":
    main()
