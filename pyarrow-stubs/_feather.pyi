from typing import Any

import pyarrow.lib

class FeatherError(Exception): ...

class FeatherReader(pyarrow.lib._Weakrefable):
    version: Any
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...
    def read(self) -> Any: ...
    def read_indices(self, indices) -> Any: ...
    def read_names(self, names) -> Any: ...
    def __reduce__(self) -> Any: ...
    def __setstate__(self, state) -> Any: ...

def tobytes(o) -> Any: ...
def write_feather(
    Tabletable, dest, compression=..., compression_level=..., chunksize=..., version=...
) -> Any: ...
