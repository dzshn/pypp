# pypp documentation

## Environment variables

- `PYPP_DEBUG`: When set to a non-empty string, enable `pypp` debug mode, which
will cause pypp to send the processed code to stdout.
- `PYPATH`: A list of directories to look for header files, separated by a
special character. This special character is platform-dependent. On most
platforms it is a colon, while on Windows it is a semicolon.

## Syntax

On top of Python syntax, `pypp` currently adds the following directives

### Including files: `!include`

`!include file.h` will replace that directive with the contents of the file. The
filename may be quoted if spaces are present (which would be otherwise ignored).

By convention, the extension for header files is either `.h` or `.hpy`.

`pypp` will search both the current directory and `PYPATH` for header files.

### Macro definitions: `!define`

In short: `!define X Y` will replace all instances of the token `X` with `Y`.

A token may be an identifier, keyword, or even operator. `Y` may also be empty,
which is equivalent to removing all instances of `X`.

Multi-token matching can be done by surrounding `X` with backticks. That is,
``!define `<>` != `` will replace all instances of `<>` (`<` and `>` glued
together) with `!=`.

It is also important to note whitespace will be ignored wherever Python also
ignores it: `<>` will also match `< >` or `<         >` (but not a newline)

### Special token escapes

- `?INDENT`: adds one indentation level
- `?DEDENT`: removes one indentation level
- `?NEWLINE`: delimits a physical line (v.s. `?NL`)
- `?NL`: delimits a logical newline (v.s. `?NEWLINE`, roughly same effect as a backslash)
- `?BACKTICK`: equivalent to a single backtick `` ` ``

More information on the distinction in physical vs logical newlines can be found [here](https://docs.python.org/3/reference/lexical_analysis.html#line-structure)
