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

SEE ALSO
    cpp(1) - A generic text preprocessor.

COPYRIGHT
    Copyright (c) 2022 Sofia Lima.  See LICENSE file for full licensing info.
"""

import re
import tokenize
from collections.abc import Callable, Iterable, Iterator
from typing import Optional, TypeVar, Union


__all__ = ["match_token", "preprocess"]

T_co = TypeVar("T_co", covariant=True)

Token = Union[tokenize.TokenInfo, tuple[int, str]]

DEFINE: list[Token] = [(tokenize.ERRORTOKEN, "!"), (tokenize.NAME, "define")]
SILLY: Token = (tokenize.ERRORTOKEN, " ")
WIDE_DEF: Token = (tokenize.ERRORTOKEN, "`")
TOKEN_ESCAPE: Token = (tokenize.ERRORTOKEN, "?")
ESCAPES: dict[str, Token] = {
    "INDENT": (tokenize.INDENT, "    "),
    "DEDENT": (tokenize.DEDENT, ""),
    "NEWLINE": (tokenize.NEWLINE, "\n"),
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

    def skip(self, n: int = 1):
        for _ in range(n):
            next(self)


def match_token(
    tokens: LookAhead[Token], query: Iterable[Token]
) -> Optional[list[Token]]:
    match: list[Token] = []
    for i, x in enumerate(query):
        try:
            if tokens.lookahead(i)[0:2] != x[0:2]:
                return None
        except StopIteration:
            return None
        match.append(x)
    return match


def to_readline(content: bytes) -> Callable[[], bytes]:
    """Trick tokenize into thinking you have a real readline method"""
    def inner() -> Iterator[bytes]:
        yield from content.splitlines(keepends=True)
        yield b""

    return inner().__next__


def preprocess(src: bytes) -> bytes:
    # comment out this line to get a lovely 1 million characters long traceback
    src = re.sub(rb"^#.*coding\w*[:=]\w*pypp.*\n", b"", src, re.M)

    tokens = LookAhead(tokenize.tokenize(to_readline(src)))

    definitions: dict[tuple[Token, ...], list[Token]] = {}
    new_tokens: list[Token] = []
    for token in tokens:
        if match_token(tokens, DEFINE):
            tokens.skip(2)
            definition: list[Token] = []
            while tokens.lookahead()[0] not in {tokenize.NEWLINE, tokenize.NL}:
                token = next(tokens)
                if token[0:2] == SILLY:
                    continue
                if token[0:2] == TOKEN_ESCAPE:
                    definition.append(ESCAPES[next(tokens)[1]])
                    continue
                definition.append(token[0:2])
            if definition[0][0:2] == WIDE_DEF:
                ident: list[Token] = []
                for tok in definition[1:]:
                    if tok == WIDE_DEF:
                        repl = definition[len(ident)+2:]
                        break
                    ident.append(tok)
                else:
                    raise SyntaxError("expected ` to close definition")
            else:
                ident = [definition[0]]
                repl = definition[1:]

            definitions[tuple(ident)] = repl
        else:
            new_tokens.append(token)
            for d, repl in definitions.items():
                if match_token(tokens, d):
                    tokens.skip(len(d))
                    new_tokens.extend(repl)
                    break

    new_src = tokenize.untokenize(i[0:2] for i in new_tokens)
    return new_src


def setup():
    from pypp._codec import register

    register()
