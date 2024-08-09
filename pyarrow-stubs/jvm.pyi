from _typeshed import Incomplete
from pyarrow.lib import Array
from pyarrow.lib import Buffer
from pyarrow.lib import Field
from pyarrow.lib import RecordBatch
from pyarrow.lib import Schema

class _JvmBufferNanny:
    ref_manager: Incomplete
    def __init__(self, jvm_buf) -> None: ...
    def __del__(self) -> None: ...

def jvm_buffer(jvm_buf) -> Buffer: ...
def field(jvm_field) -> Field: ...
def schema(jvm_schema) -> Schema: ...
def array(jvm_array) -> Array: ...
def record_batch(jvm_vector_schema_root) -> RecordBatch: ...
