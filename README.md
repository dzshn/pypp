# pypp - The Python Preprocessor

```py
##define coding=pypp

!define { :?NEWLINE?INDENT
!define } ?NEWLINE?DEDENT
!define fn def
!define `println!` print
!define ?ENDMARKER main()?ENDMARKER

fn main() {
    println!("hai :3");
}
```

## Features

- Extremely flexible and easy to use token-based macros: `!define PI 3` is just as valid as ``!define `<>` !=``.
- Completely compatible with all Python code, the syntax for directives is superset from it.
    - Imports work both ways
    - On many cases, also compatible with code checking tools (type checking with `mypy` works)

## Roadmap

- Constants (e.g. by platform)
- Conditional compilation (e.g. `!if sys.platform == "linux":`)
- Custom pragmas
- Automatic `.pth` installation (possibly like [`pyston_lite_autoload`](https://github.com/pyston/pyston/blob/main/pyston/pyston_lite/autoload/setup.py))
- PyPy support

## Install

Install with pip: (only requires python >= 3.9)

```sh
$ pip install git+https://github.com/dzshn/pypp
# or `py -m pip` etc
```

From source using [poetry](https://python-poetry.org):
```sh
$ poetry install
```

> **Warning**
> It is also required to copy over the `pypp_autoload.pth` file into `site-packages` (see section below).

## Usage

To autoload `pypp`, it is required to copy over the `pypp_autoload.pth` file into your
site-packages. By default, Python uses the following paths: _(X and Y refer to Python's
version)_

- Unix: `~/.local/lib/pythonX.Y/site-packages`
- macOS: `~/Library/Python/X.Y/lib/python/site-packages`
- Windows: `%APPDATA%\Python\PythonXY\site-packages`

Loading can also be done manually by calling `pypp.setup()`.

`pypp` is also available programmatically via `pypp.preprocess(src: bytes) -> bytes`.

Usage examples can be found [here](examples/). More in-depth documentation can be found [here](DOCS.md)

## wait, what

good question!

## the How

the file is preprocessed in a C-like fashion, with some things added here and
there. that part of the code is relatively[^1][^2] "normal". to trick python into
thinking macros are real, though, requires a custom encoding to be made and
loaded *before* python executes the script, (see [dankeyy's indec.py](https://github.com/dankeyy/incdec.py)
for prior art) which allows preprocessing to happen right before python does
tokenization, thus avoiding all syntax errors.

this could also potentially be implemented by hooking into `sys.meta_path`,
but I thought doing stuff before tokenization was infinitely sillier :3

[^1]: [Lispy](https://github.com/dzshn/lispy), a lisp dialect that's also valid python
[^2]: [uwu](https://github.com/dzshn/uwu), `(^·ω·^)`-ified python bytecode
