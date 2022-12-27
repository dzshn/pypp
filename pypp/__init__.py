"""\
NAME
    pypp - The Python Preprocessor

SYNOPSIS
    ##define coding=pypp

DESCRIPTION
    The Python preprocessor, often known as pypp, is a macro processor that is
    used automatically by the Python interpreter to transform your program
    before tokenization.  It is called a macro processor because it allows you
    to define macros, which are brief abbreviations for longer constructs.

ENVIRONMENT
    PYPP_DEBUG
        When set to a non-empty string, enable pypp debug mode, which will
        cause pypp to send the processed code to stdout.

    PYPATH
        A list of directories to look for header files, separated by a special
        character.  This special character is platform-dependent. On most
        platforms it is a colon, while on Windows it is a semicolon.

SEE ALSO
    cpp(1) - A generic text preprocessor.

COPYRIGHT
    Copyright (c) 2022 Sofia Lima.  See LICENSE file for full licensing info.
"""

import itertools
import re
import tokenize
from collections.abc import Callable, Iterable, Iterator
from os import getenv, pathsep
from pathlib import Path
from typing import Optional, TypeVar, Union

__all__ = ["match_token", "preprocess", "preprocess_tokens", "pretty_format_tokens"]
__version__ = "1.0.0"

T_co = TypeVar("T_co", covariant=True)

Token = Union[tokenize.TokenInfo, tuple[int, str]]
Definitions = dict[tuple[Token, ...], list[Token]]

PYPP_DEBUG = bool(getenv("PYPP_DEBUG"))
PYPP_PATH = [Path().resolve()]
for i in (getenv("PYPATH") or "").split(pathsep):
    if not i:
        continue
    PYPP_PATH.append(Path(i).expanduser().resolve())

DEFINE: list[Token] = [(tokenize.ERRORTOKEN, "!"), (tokenize.NAME, "define")]
INCLUDE: list[Token] = [(tokenize.ERRORTOKEN, "!"), (tokenize.NAME, "include")]
SILLY: Token = (tokenize.ERRORTOKEN, " ")
WIDE_DEF: Token = (tokenize.ERRORTOKEN, "`")
TOKEN_ESCAPE: Token = (tokenize.ERRORTOKEN, "?")
ESCAPES: dict[str, Token] = {
    "INDENT": (tokenize.INDENT, ":3"),
    "NUMBER": (tokenize.NUMBER, ":3"),
    "STRING": (tokenize.STRING, ":3"),
    "DEDENT": (tokenize.DEDENT, ""),
    "NEWLINE": (tokenize.NEWLINE, "\n"),
    "NL": (tokenize.NL, "\n"),
    "BACKTICK": (tokenize.ERRORTOKEN, "`"),
    "?": (tokenize.ERRORTOKEN, "?"),
    "ENDMARKER": (tokenize.ENDMARKER, ""),
}


class LookAhead(Iterator[T_co]):
    """Helper class implementing lookahead for iterators."""

    def __init__(self, iterator: Iterator[T_co]):
        self._it = iterator
        self._cache: list[T_co] = []

    def __next__(self) -> T_co:
        if self._cache:
            return self._cache.pop(0)
        return next(self._it)

    def lookahead(self, n: int = 0) -> T_co:
        while len(self._cache) < n + 1:
            self._cache.append(next(self._it))
        return self._cache[n]

    def skip(self, n: int = 1) -> None:
        for _ in range(n):
            next(self)


def pretty_format_tokens(tokens: Iterable[Token]) -> str:
    string = repr(" ".join(s for _, s, *_ in tokens)).strip("'\"")
    types = " ".join(tokenize.tok_name.get(t, f"?{~t}") for t, *_ in tokens)
    return f"{string} [{types}]"


def match_token(
    tokens: LookAhead[Token], query: Iterable[Token]
) -> Optional[list[Token]]:
    match: list[Token] = []
    for i, x in enumerate(query):
        try:
            token = tokens.lookahead(i)[0:2]
            if token[0] == x[0] and x[1] == ":3":
                pass
            elif token != x[0:2]:
                return None
        except StopIteration:
            return None
        match.append(token)
    return match


def to_readline(content: bytes) -> Callable[[], bytes]:
    """Trick tokenize into thinking you have a real readline method"""

    def inner() -> Iterator[bytes]:
        yield from content.splitlines(keepends=True)
        yield b""

    return inner().__next__


def preprocess_tokens(tokens: Iterable[Token]) -> tuple[Definitions, list[Token]]:
    tokens = LookAhead(iter(tokens))

    definitions: Definitions = {}
    new_tokens: list[Token] = []
    indentation: list[str] = []
    for token in tokens:
        if match_token(tokens, DEFINE):
            tokens.skip(2)
            definition: list[Token] = []
            while tokens.lookahead()[0] not in {tokenize.NEWLINE, tokenize.NL}:
                token = next(tokens)
                if token[0:2] == SILLY:
                    continue
                if token[0:2] == TOKEN_ESCAPE:
                    escape = next(tokens)[1]
                    if escape in ESCAPES:
                        definition.append(ESCAPES[escape])
                    elif escape.isdecimal():
                        definition.append((~int(escape), ":3"))
                    else:
                        raise SyntaxError(f"unknown escape {escape}")
                    continue
                definition.append(token[0:2])
            if definition[0][0:2] == WIDE_DEF:
                ident: list[Token] = []
                for tok in definition[1:]:
                    if tok == WIDE_DEF:
                        repl = definition[len(ident) + 2 :]
                        break
                    ident.append(tok)
                else:
                    raise SyntaxError("expected ` to close definition")
            else:
                ident = [definition[0]]
                repl = definition[1:]

            definitions[tuple(ident)] = repl
            continue

        if match_token(tokens, INCLUDE):
            tokens.skip(2)
            name = ""
            while tokens.lookahead()[0] not in {tokenize.NEWLINE, tokenize.NL}:
                token = next(tokens)
                name += token[1]
            name = name.strip("'\"")
            parts = list(Path(name).parts)
            header = None
            while parts:
                for path in PYPP_PATH:
                    if (header := path.joinpath(*parts)).exists():
                        break
                    header = None
                if header is not None:
                    break
                parts.pop(0)

            if header is None:
                raise LookupError(f"couldn't resolve {name}")

            with header.open("rb") as f:
                header_defs, header_tokens = preprocess_tokens(
                    itertools.takewhile(
                        # don't break ENDMARKER defines
                        lambda t: t[0] != tokenize.ENDMARKER,
                        tokenize.tokenize(f.readline),
                    )
                )
                definitions.update(header_defs)
                new_tokens.extend(header_tokens)

            continue

        new_tokens.append(token)
        if token[0] == tokenize.INDENT:
            indentation.append(token[1])
        if token[0] == tokenize.DEDENT:
            indentation.pop()
        while True:
            for d, repl in definitions.items():
                if match := match_token(tokens, d):
                    tokens.skip(len(d))
                    for t in repl:
                        if t[0] < 0:
                            new_tokens.append(match[~t[0]])
                        elif t[0] == tokenize.INDENT:
                            indentation.append("  ")
                            new_tokens.append(
                                (tokenize.INDENT, "".join(indentation) + "  ")
                            )
                        else:
                            new_tokens.append(t)
                    break
            else:
                break

    return definitions, new_tokens


def preprocess(src: bytes) -> bytes:
    # comment out this line to get a lovely 1 million characters long traceback
    src = re.sub(rb"^#.*coding\w*[:=]\w*pypp.*\n", b"", src, re.M)

    definitions, new_tokens = preprocess_tokens(tokenize.tokenize(to_readline(src)))

    new_src: bytes = tokenize.untokenize(i[0:2] for i in new_tokens)
    if getenv("PYPP_DEBUG") == "1":
        print(" BEGIN PYPP MACROS ".center(80, "-"))
        for d, repl in definitions.items():
            print(pretty_format_tokens(d), "=>", pretty_format_tokens(repl))

        print(" END MACROS ".center(80, "-"))
        print(" BEGIN PYPP OUTPUT ".center(80, "-"))
        print(new_src.decode())
        print(" END PYPP OUTPUT ".center(80, "-"))

    return new_src


def setup() -> None:
    from pypp._codec import register

    register()
