# jp-dict

A command-line Japanese-English dictionary.
This is a work in progress, results not guaranteed.
Feedback and suggestions are appreciated.

## Installation

To install, clone the git repository, then build the package and install with pip and update the dictionary files:
```console
$ git clone https://github.com/matyanwek/jp-dict
$ cd jp-dict
$ python3 setup.py bdist_wheel
$ pip3 install .
$ jp-dict --update
```

The cloned git directory can then be deleted.

To uninstall, clean the dictionary files, then use pip:
```console
$ jp-dict --clean
$ pip3 uninstall jp-dict
```

## Usage

Update and re-index the dictionary:
```console
$ jp-dict --update
```

Search (English or Japanese), print first result:
```console
$ jp-dict query words go here
```

Search (English or Japanese), print all results:
```console
$ jp-dict --all query words go here
```

Start the persistent REPL:
```console
$ jp-dict
jp>
```
