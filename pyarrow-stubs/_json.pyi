from typing import (
    Any,
    ClassVar,
)

import pyarrow.lib

class ParseOptions(pyarrow.lib._Weakrefable):
    __slots__: ClassVar[tuple] = ...
    explicit_schema: Any
    newlines_in_values: Any
    unexpected_field_behavior: Any
    def __init__(self, *args, **kwargs) -> None: ...
    def __reduce__(self) -> Any: ...

class ReadOptions(pyarrow.lib._Weakrefable):
    __slots__: ClassVar[tuple] = ...
    block_size: Any
    use_threads: Any
    def __init__(self, *args, **kwargs) -> None: ...
    def __reduce__(self) -> Any: ...

def read_json(
    input_file, read_options=..., parse_options=..., MemoryPoolmemory_pool=...
) -> Any: ...
