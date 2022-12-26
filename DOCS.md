# pypp documentation

## Syntax

On top of Python syntax, `pypp` currently adds the following directives

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
