# pypp - the python preprocessor

```py
##define coding=pypp

!define { :?NEWLINE?INDENT
!define } ?NEWLINE?DEDENT

while (True) {
    print(":3");
}
```

## Features

- Entirely token-based, like `cpp`
- Macro definitions (`!define PI 3`)
- Multi-token replacement (``!define `<>` !=``)
- Probably production ready

## Roadmap

- [ ] Constants (e.g. `_WIN32`)
- [ ] Conditionals (`!ifdef`, `!ifndef`)
- [ ] Includes (`!include file.h`)
- [ ] Custom pragmas
- [x] Better `INDENT` token handling
- [ ] Automatically install `.pth` file (possibly like [`pyston_lite_autoload`](https://github.com/pyston/pyston/blob/main/pyston/pyston_lite/autoload/setup.py))

## Install

Install with pip: (only requires python >= 3.9)

```sh
$ pip install git+https://github.com/dzshn/pypp
# or `py -m pip` etc
```

From source using [poetry](https://python-poetry.org)
```sh
$ poetry install
```

## Usage

Call `pypp.setup()`, which will register the `pypp` codec. After that, you can
import any file with the appropriate header (e.g. `##define coding=pypp`). This can
be done automatically on every startup by copying the `pypp_autoload.pth` file into
`site-packages`. (e.g. on linux: `~/.local/lib/python3.10/site-packages`)

pypp is also available programmatically via `pypp.preprocess(src: bytes) -> bytes`.

## wait, what

good question!

## the How

the file is preprocessed in a C-like fashion, with some things added here and
there. that part of the code is relatively "normal". to trick python into
thinking macros are real, though, requires a custom encoding to be made and
loaded *before* python executes the script, (see [dankeyy's indec.py](https://github.com/dankeyy/incdec.py)
for prior art) which allows preprocessing to happen right before python does
tokenization, thus avoiding all syntax errors.

this could also potentially be implemented by hooking into `sys.meta_path`,
but I thought doing stuff before tokenization was infinitely sillier :3
