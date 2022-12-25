import codecs
import traceback
from typing import Optional, Union

from pypp import preprocess


class PYPPCodec(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input: bytes, errors: str, final: bool) -> tuple[str, int]:  # type: ignore
        if input:
            return decode(input)
        return "", 0


def explode(input: str, errors: str = "strict"):
    raise NotImplementedError


def decode(input: Union[memoryview, bytes], errors: str = "strict") -> tuple[str, int]:
    if isinstance(input, memoryview):
        input = input.tobytes()
    try:
        return preprocess(input).decode(), len(input)
    except Exception:
        # be nice and manually print the traceback because python throws it
        # into the void and simply says `encoding problem` instead
        traceback.print_exc()
        raise


def search_function(name: str) -> Optional[codecs.CodecInfo]:
    if name == "pypp":
        return codecs.CodecInfo(
            explode,
            decode,
            incrementaldecoder=PYPPCodec,
            name="pypp"
        )
    return None


def register() -> None:
    codecs.register(search_function)
