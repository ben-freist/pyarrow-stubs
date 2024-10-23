import datetime as dt
import sys

from collections.abc import Mapping
from decimal import Decimal

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from typing import Any, Generic, Iterable, Iterator, Literal, overload

import numpy as np
import pandas as pd

from pyarrow._stubs_typing import SupportArrowSchema
from pyarrow.lib import (
    Array,
    ChunkedArray,
    ExtensionArray,
    MemoryPool,
    MonthDayNano,
    Table,
)
from typing_extensions import TypeVar

from .io import Buffer
from .scalar import ExtensionScalar

_AsPyType = TypeVar("_AsPyType")
_DataTypeT = TypeVar("_DataTypeT", bound=DataType)
_DataType_CoT = TypeVar("_DataType_CoT", bound=DataType, covariant=True)

class _Weakrefable: ...
class _Metadata(_Weakrefable): ...

class DataType(_Weakrefable):
    def field(self, i: int) -> Field: ...
    @property
    def id(self) -> int: ...
    @property
    def bit_width(self) -> int: ...
    @property
    def byte_width(self) -> int: ...
    @property
    def num_fields(self) -> int: ...
    @property
    def num_buffers(self) -> int: ...
    def __hash__(self) -> int: ...
    def equals(self, other: DataType | str, *, check_metadata: bool = False) -> bool: ...
    def to_pandas_dtype(self) -> np.generic: ...
    def _export_to_c(self, out_ptr: int) -> None: ...
    @classmethod
    def _import_from_c(cls, in_ptr: int) -> Self: ...
    def __arrow_c_schema__(self) -> Any: ...
    @classmethod
    def _import_from_c_capsule(cls, schema) -> Self: ...

class _BasicDataType(DataType, Generic[_AsPyType]): ...
class NullType(_BasicDataType[None]): ...
class BoolType(_BasicDataType[bool]): ...
class Uint8Type(_BasicDataType[int]): ...
class Int8Type(_BasicDataType[int]): ...
class Uint16Type(_BasicDataType[int]): ...
class Int16Type(_BasicDataType[int]): ...
class Uint32Type(_BasicDataType[int]): ...
class Int32Type(_BasicDataType[int]): ...
class Uint64Type(_BasicDataType[int]): ...
class Int64Type(_BasicDataType[int]): ...
class Float16Type(_BasicDataType[float]): ...
class Float32Type(_BasicDataType[float]): ...
class Float64Type(_BasicDataType[float]): ...
class Date32Type(_BasicDataType[dt.date]): ...
class Date64Type(_BasicDataType[dt.date]): ...
class MonthDayNanoIntervalType(_BasicDataType[MonthDayNano]): ...
class StringType(_BasicDataType[str]): ...
class LargeStringType(_BasicDataType[str]): ...
class StringViewType(_BasicDataType[str]): ...
class BinaryType(_BasicDataType[bytes]): ...
class LargeBinaryType(_BasicDataType[bytes]): ...
class BinaryViewType(_BasicDataType[bytes]): ...

_Unit = TypeVar("_Unit", bound=Literal["s", "ms", "us", "ns"])
_Tz = TypeVar("_Tz", str, None, default=None)

class TimestampType(_BasicDataType[int], Generic[_Unit, _Tz]):
    @property
    def unit(self) -> _Unit: ...
    @property
    def tz(self) -> _Tz: ...

_Time32Unit = TypeVar("_Time32Unit", bound=Literal["s", "ms"])

class Time32Type(_BasicDataType[dt.time], Generic[_Time32Unit]):
    @property
    def unit(self) -> _Time32Unit: ...

_Time64Unit = TypeVar("_Time64Unit", bound=Literal["us", "ns"])

class Time64Type(_BasicDataType[dt.time], Generic[_Time64Unit]):
    @property
    def unit(self) -> _Time64Unit: ...

class DurationType(_BasicDataType[dt.timedelta], Generic[_Unit]):
    @property
    def unit(self) -> _Unit: ...

class FixedSizeBinaryType(_BasicDataType[Decimal]): ...

_Precision = TypeVar("_Precision")
_Scale = TypeVar("_Scale")

class Decimal128Type(FixedSizeBinaryType, Generic[_Precision, _Scale]):
    @property
    def precision(self) -> _Precision: ...
    @property
    def scale(self) -> _Scale: ...

class Decimal256Type(FixedSizeBinaryType, Generic[_Precision, _Scale]):
    @property
    def precision(self) -> _Precision: ...
    @property
    def scale(self) -> _Scale: ...

class ListType(DataType, Generic[_DataType_CoT]):
    @property
    def value_field(self) -> Field[_DataType_CoT]: ...
    @property
    def value_type(self) -> _DataType_CoT: ...

class LargeListType(ListType[_DataType_CoT]): ...
class ListViewType(ListType[_DataType_CoT]): ...
class LargeListViewType(ListType[_DataType_CoT]): ...

class FixedSizeListType(ListType[_DataType_CoT], Generic[_DataType_CoT, _Size]):
    @property
    def list_size(self) -> _Size: ...

class DictionaryMemo(_Weakrefable): ...

_IndexT = TypeVar(
    "_IndexT",
    Uint8Type,
    Int8Type,
    Uint16Type,
    Int16Type,
    Uint32Type,
    Int32Type,
    Uint64Type,
    Int64Type,
)
_BasicValueT = TypeVar("_BasicValueT", bound=_BasicDataType)
_ValueT = TypeVar("_ValueT", bound=DataType)
_Ordered = TypeVar("_Ordered", bound=Literal[True, False], default=Literal[False])

class DictionaryType(DataType, Generic[_IndexT, _BasicValueT, _Ordered]):
    @property
    def ordered(self) -> _Ordered: ...
    @property
    def index_type(self) -> _IndexT: ...
    @property
    def value_type(self) -> _BasicValueT: ...

_K = TypeVar("_K", bound=DataType)

class MapType(DataType, Generic[_K, _ValueT, _Ordered]):
    @property
    def key_field(self) -> Field[_K]: ...
    @property
    def key_type(self) -> _K: ...
    @property
    def item_field(self) -> Field[_ValueT]: ...
    @property
    def item_type(self) -> _ValueT: ...
    @property
    def keys_sorted(self) -> _Ordered: ...

_Size = TypeVar("_Size")

class StructType(DataType):
    def get_field_index(self, name: str) -> int: ...
    def field(self, i: int | str) -> Field: ...
    def get_all_field_indices(self, name: str) -> list[int]: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Field]: ...
    __getitem__ = field

class UnionType(DataType):
    @property
    def mode(self) -> Literal["sparse", "dense"]: ...
    @property
    def type_codes(self) -> list[int]: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Field]: ...
    def field(self, i: int) -> Field: ...
    __getitem__ = field

class SparseUnionType(UnionType):
    @property
    def mode(self) -> Literal["sparse"]: ...

class DenseUnionType(UnionType):
    @property
    def mode(self) -> Literal["dense"]: ...

_RunEndType = TypeVar("_RunEndType", Int16Type, Int32Type, Int64Type)

class RunEndEncodedType(DataType, Generic[_RunEndType, _BasicValueT]):
    @property
    def run_end_type(self) -> _RunEndType: ...
    @property
    def value_type(self) -> _BasicValueT: ...

_StorageT = TypeVar("_StorageT", bound=Array | ChunkedArray)

class BaseExtensionType(DataType):
    def __arrow_ext_class__(self) -> type[ExtensionArray]: ...
    def __arrow_ext_scalar_class__(self) -> type[ExtensionScalar]: ...
    @property
    def extension_name(self) -> str: ...
    @property
    def storage_type(self) -> DataType: ...
    def wrap_array(self, storage: _StorageT) -> _StorageT: ...

class ExtensionType(BaseExtensionType):
    def __init__(self, storage_type: DataType, extension_name: str) -> None: ...
    def __arrow_ext_serialize__(self) -> bytes: ...
    @classmethod
    def __arrow_ext_deserialize__(cls, storage_type: DataType, serialized: bytes) -> Self: ...

class FixedShapeTensorType(BaseExtensionType, Generic[_ValueT]):
    @property
    def value_type(self) -> _ValueT: ...
    @property
    def shape(self) -> list[int]: ...
    @property
    def dim_names(self) -> list[str] | None: ...
    @property
    def permutation(self) -> list[int] | None: ...

class PyExtensionType(ExtensionType):
    def __init__(self, storage_type: DataType) -> None: ...
    @classmethod
    def set_auto_load(cls, value: bool) -> None: ...

class UnknownExtensionType(PyExtensionType):
    def __init__(self, storage_type: DataType, serialized: bytes) -> None: ...

def register_extension_type(ext_type: PyExtensionType) -> None: ...
def unregister_extension_type(type_name: str) -> None: ...

class KeyValueMetadata(_Metadata, Mapping[bytes, bytes]):
    def __init__(self, __arg0__: Mapping[bytes, bytes] | None = None, **kwargs) -> None: ...
    def equals(self, other: KeyValueMetadata) -> bool: ...
    def __len__(self) -> int: ...
    def __contains__(self, __key: object) -> bool: ...
    def __getitem__(self, __key: Any) -> Any: ...
    def __iter__(self) -> Iterator[bytes]: ...
    def get_all(self, key: str) -> list[bytes]: ...
    def to_dict(self) -> dict[bytes, bytes]: ...

def ensure_metadata(
    meta: Mapping[bytes | str, bytes | str] | KeyValueMetadata | None, allow_none: bool = False
) -> KeyValueMetadata | None: ...

class Field(_Weakrefable, Generic[_DataType_CoT]):
    def equals(self, other: Field, check_metadata: bool = False) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def nullable(self) -> bool: ...
    @property
    def name(self) -> str: ...
    @property
    def metadata(self) -> dict[bytes, bytes] | None: ...
    @property
    def type(self) -> _DataType_CoT: ...
    def with_metadata(self, metadata: dict[bytes | str, bytes | str]) -> Self: ...
    def remove_metadata(self) -> None: ...
    def with_type(self, new_type: _DataTypeT) -> Field[_DataTypeT]: ...
    def with_name(self, name: str) -> Self: ...
    def with_nullable(self, nullable: bool) -> Field[_DataType_CoT]: ...
    def flatten(self) -> list[Field]: ...
    def _export_to_c(self, out_ptr: int) -> None: ...
    @classmethod
    def _import_from_c(cls, in_ptr: int) -> Self: ...
    def __arrow_c_schema__(self) -> Any: ...
    @classmethod
    def _import_from_c_capsule(cls, schema) -> Self: ...

class Schema(_Weakrefable):
    def __len__(self) -> int: ...
    def __getitem__(self, key: str) -> Field: ...
    _field = __getitem__
    def __iter__(self) -> Iterator[Field]: ...
    def __hash__(self) -> int: ...
    def __sizeof__(self) -> int: ...
    @property
    def pandas_metadata(self) -> dict: ...
    @property
    def names(self) -> list[str]: ...
    @property
    def types(self) -> list[DataType]: ...
    @property
    def metadata(self) -> dict[bytes, bytes]: ...
    def empty_table(self) -> Table: ...
    def equals(self, other: Schema, check_metadata: bool = False) -> bool: ...
    @classmethod
    def from_pandas(cls, df: pd.DataFrame, preserve_index: bool | None = None) -> Schema: ...
    def field(self, i: int | str | bytes) -> Field: ...
    def field_by_name(self, name: str) -> Field: ...
    def get_field_index(self, name: str) -> int: ...
    def get_all_field_indices(self, name: str) -> list[int]: ...
    def append(self, field: Field) -> Schema: ...
    def insert(self, i: int, field: Field) -> Schema: ...
    def remove(self, i: int) -> Schema: ...
    def set(self, i: int, field: Field) -> Schema: ...
    def add_metadata(self, metadata: dict) -> Schema: ...
    def with_metadata(self, metadata: dict) -> Schema: ...
    def serialize(self, memory_pool: MemoryPool | None = None) -> Buffer: ...
    def remove_metadata(self) -> Schema: ...
    def to_string(
        self,
        truncate_metadata: bool = True,
        show_field_metadata: bool = True,
        show_schema_metadata: bool = True,
    ) -> str: ...
    def _export_to_c(self, out_ptr: int) -> None: ...
    @classmethod
    def _import_from_c(cls, in_ptr: int) -> Schema: ...
    def __arrow_c_schema__(self) -> Any: ...
    @staticmethod
    def _import_from_c_capsule(schema: Any) -> Schema: ...

def unify_schemas(
    schemas: list[Schema], *, promote_options: Literal["default", "permissive"] = "default"
) -> Schema: ...
@overload
def field(name: SupportArrowSchema) -> Field: ...
@overload
def field(
    name: str, type: _DataTypeT, nullable: bool = ..., metadata: dict | None = None
) -> Field[_DataTypeT]: ...
def null() -> NullType: ...
def bool_() -> BoolType: ...
def uint8() -> Uint8Type: ...
def int8() -> Int8Type: ...
def uint16() -> Uint16Type: ...
def int16() -> Int16Type: ...
def uint32() -> Uint32Type: ...
def int32() -> Int32Type: ...
def int64() -> Int64Type: ...
def uint64() -> Uint64Type: ...
def tzinfo_to_string(tz: dt.tzinfo) -> str: ...
def string_to_tzinfo(name: str) -> dt.tzinfo: ...
@overload
def timestamp(unit: _Unit) -> TimestampType[_Unit, None]: ...
@overload
def timestamp(unit: _Unit, tz: _Tz) -> TimestampType[_Unit, _Tz]: ...
def time32(unit: _Time32Unit) -> Time32Type[_Time32Unit]: ...
def time64(unit: _Time64Unit) -> Time64Type[_Time64Unit]: ...
def duration(unit: _Unit) -> DurationType[_Unit]: ...
def month_day_nano_interval() -> MonthDayNanoIntervalType: ...
def date32() -> Date32Type: ...
def date64() -> Date64Type: ...
def float16() -> Float16Type: ...
def float32() -> Float32Type: ...
def float64() -> Float64Type: ...
@overload
def decimal128(precision: _Precision) -> Decimal128Type[_Precision, Literal[0]]: ...
@overload
def decimal128(precision: _Precision, scale: _Scale) -> Decimal128Type[_Precision, _Scale]: ...
@overload
def decimal256(precision: _Precision) -> Decimal256Type[_Precision, Literal[0]]: ...
@overload
def decimal256(precision: _Precision, scale: _Scale) -> Decimal256Type[_Precision, _Scale]: ...
def string() -> StringType: ...

utf8 = string

@overload
def binary() -> BinaryType: ...
@overload
def binary(length: Literal[-1]) -> BinaryType: ...  # type: ignore[overload-overlap]
@overload
def binary(length: int) -> FixedSizeBinaryType: ...
def large_binary() -> LargeBinaryType: ...
def large_string() -> LargeStringType: ...

large_utf8 = large_string

def binary_view() -> BinaryViewType: ...
def string_view() -> StringViewType: ...
@overload
def list_(value_type: Field[_DataTypeT]) -> ListType[_DataTypeT]: ...
@overload
def list_(value_type: _DataTypeT) -> ListType[_DataTypeT]: ...
@overload
def list_(value_type: _DataTypeT, list_size: Literal[-1]) -> ListType[_DataTypeT]: ...  # type: ignore[overload-overlap]
@overload
def list_(value_type: _DataTypeT, list_size: _Size) -> FixedSizeListType[_DataTypeT, _Size]: ...
@overload
def large_list(value_type: Field[_DataTypeT]) -> LargeListType[_DataTypeT]: ...
@overload
def large_list(value_type: _DataTypeT) -> LargeListType[_DataTypeT]: ...
@overload
def list_view(value_type: Field[_DataTypeT]) -> ListViewType[_DataTypeT]: ...
@overload
def list_view(value_type: _DataTypeT) -> ListViewType[_DataTypeT]: ...
@overload
def large_list_view(value_type: Field[_DataTypeT]) -> LargeListViewType[_DataTypeT]: ...
@overload
def large_list_view(value_type: _DataTypeT) -> LargeListViewType[_DataTypeT]: ...
@overload
def map_(key_type: _K, item_type: _ValueT) -> MapType[_K, _ValueT, Literal[False]]: ...
@overload
def map_(
    key_type: _K, item_type: _ValueT, key_sorted: _Ordered
) -> MapType[_K, _ValueT, _Ordered]: ...
@overload
def dictionary(
    index_type: _IndexT, value_type: _BasicValueT
) -> DictionaryType[_IndexT, _BasicValueT, Literal[False]]: ...
@overload
def dictionary(
    index_type: _IndexT, value_type: _BasicValueT, ordered: _Ordered
) -> DictionaryType[_IndexT, _BasicValueT, _Ordered]: ...
def struct(
    fields: Iterable[Field | tuple[str, Field]] | Mapping[str, Field],
) -> StructType: ...
def sparse_union(
    child_fields: list[Field], type_codes: list[int] | None = None
) -> SparseUnionType: ...
def dense_union(
    child_fields: list[Field], type_codes: list[int] | None = None
) -> DenseUnionType: ...
@overload
def union(
    child_fields: list[Field], mode: Literal["sparse"], type_codes: list[int] | None = None
) -> SparseUnionType: ...
@overload
def union(
    child_fields: list[Field], mode: Literal["dense"], type_codes: list[int] | None = None
) -> DenseUnionType: ...
def run_end_encoded(
    run_end_type: _RunEndType, value_type: _BasicValueT
) -> RunEndEncodedType[_RunEndType, _BasicValueT]: ...
def fixed_shape_tensor(
    value_type: _ValueT,
    shape: tuple[list[int], ...],
    dim_names: tuple[list[str], ...] | None = None,
    permutation: tuple[list[int], ...] | None = None,
) -> FixedShapeTensorType[_ValueT]: ...
@overload
def type_for_alias(name: Literal["null"]) -> NullType: ...
@overload
def type_for_alias(name: Literal["bool", "boolean"]) -> BoolType: ...
@overload
def type_for_alias(name: Literal["i1", "int8"]) -> Int8Type: ...
@overload
def type_for_alias(name: Literal["i2", "int16"]) -> Int16Type: ...
@overload
def type_for_alias(name: Literal["i4", "int32"]) -> Int32Type: ...
@overload
def type_for_alias(name: Literal["i8", "int64"]) -> Int64Type: ...
@overload
def type_for_alias(name: Literal["u1", "uint8"]) -> Uint8Type: ...
@overload
def type_for_alias(name: Literal["u2", "uint16"]) -> Uint16Type: ...
@overload
def type_for_alias(name: Literal["u4", "uint32"]) -> Uint32Type: ...
@overload
def type_for_alias(name: Literal["u8", "uint64"]) -> Uint64Type: ...
@overload
def type_for_alias(name: Literal["f2", "halffloat", "float16"]) -> Float16Type: ...
@overload
def type_for_alias(name: Literal["f4", "float", "float32"]) -> Float32Type: ...
@overload
def type_for_alias(name: Literal["f8", "double", "float64"]) -> Float64Type: ...
@overload
def type_for_alias(name: Literal["string", "str", "utf8"]) -> StringType: ...
@overload
def type_for_alias(name: Literal["binary"]) -> BinaryType: ...
@overload
def type_for_alias(
    name: Literal["large_string", "large_str", "large_utf8"],
) -> LargeStringType: ...
@overload
def type_for_alias(name: Literal["large_binary"]) -> LargeBinaryType: ...
@overload
def type_for_alias(name: Literal["binary_view"]) -> BinaryViewType: ...
@overload
def type_for_alias(name: Literal["string_view"]) -> StringViewType: ...
@overload
def type_for_alias(name: Literal["date32", "date32[day]"]) -> Date32Type: ...
@overload
def type_for_alias(name: Literal["date64", "date64[ms]"]) -> Date64Type: ...
@overload
def type_for_alias(name: Literal["time32[s]"]) -> Time32Type[Literal["s"]]: ...
@overload
def type_for_alias(name: Literal["time32[ms]"]) -> Time32Type[Literal["ms"]]: ...
@overload
def type_for_alias(name: Literal["time64[us]"]) -> Time64Type[Literal["us"]]: ...
@overload
def type_for_alias(name: Literal["time64[ns]"]) -> Time64Type[Literal["ns"]]: ...
@overload
def type_for_alias(name: Literal["timestamp[s]"]) -> TimestampType[Literal["s"], Any]: ...
@overload
def type_for_alias(name: Literal["timestamp[ms]"]) -> TimestampType[Literal["ms"], Any]: ...
@overload
def type_for_alias(name: Literal["timestamp[us]"]) -> TimestampType[Literal["us"], Any]: ...
@overload
def type_for_alias(name: Literal["timestamp[ns]"]) -> TimestampType[Literal["ns"], Any]: ...
@overload
def type_for_alias(name: Literal["duration[s]"]) -> DurationType[Literal["s"]]: ...
@overload
def type_for_alias(name: Literal["duration[ms]"]) -> DurationType[Literal["ms"]]: ...
@overload
def type_for_alias(name: Literal["duration[us]"]) -> DurationType[Literal["us"]]: ...
@overload
def type_for_alias(name: Literal["duration[ns]"]) -> DurationType[Literal["ns"]]: ...
@overload
def type_for_alias(name: Literal["month_day_nano_interval"]) -> MonthDayNanoIntervalType: ...
@overload
def ensure_type(ty: None, allow_none: Literal[True]) -> None: ...
@overload
def ensure_type(ty: _DataTypeT) -> _DataTypeT: ...
@overload
def ensure_type(ty: Literal["null"]) -> NullType: ...
@overload
def ensure_type(ty: Literal["bool", "boolean"]) -> BoolType: ...
@overload
def ensure_type(ty: Literal["i1", "int8"]) -> Int8Type: ...
@overload
def ensure_type(ty: Literal["i2", "int16"]) -> Int16Type: ...
@overload
def ensure_type(ty: Literal["i4", "int32"]) -> Int32Type: ...
@overload
def ensure_type(ty: Literal["i8", "int64"]) -> Int64Type: ...
@overload
def ensure_type(ty: Literal["u1", "uint8"]) -> Uint8Type: ...
@overload
def ensure_type(ty: Literal["u2", "uint16"]) -> Uint16Type: ...
@overload
def ensure_type(ty: Literal["u4", "uint32"]) -> Uint32Type: ...
@overload
def ensure_type(ty: Literal["u8", "uint64"]) -> Uint64Type: ...
@overload
def ensure_type(ty: Literal["f2", "halffloat", "float16"]) -> Float16Type: ...
@overload
def ensure_type(ty: Literal["f4", "float", "float32"]) -> Float32Type: ...
@overload
def ensure_type(ty: Literal["f8", "double", "float64"]) -> Float64Type: ...
@overload
def ensure_type(ty: Literal["string", "str", "utf8"]) -> StringType: ...
@overload
def ensure_type(ty: Literal["binary"]) -> BinaryType: ...
@overload
def ensure_type(
    ty: Literal["large_string", "large_str", "large_utf8"],
) -> LargeStringType: ...
@overload
def ensure_type(ty: Literal["large_binary"]) -> LargeBinaryType: ...
@overload
def ensure_type(ty: Literal["binary_view"]) -> BinaryViewType: ...
@overload
def ensure_type(ty: Literal["string_view"]) -> StringViewType: ...
@overload
def ensure_type(ty: Literal["date32", "date32[day]"]) -> Date32Type: ...
@overload
def ensure_type(ty: Literal["date64", "date64[ms]"]) -> Date64Type: ...
@overload
def ensure_type(ty: Literal["time32[s]"]) -> Time32Type[Literal["s"]]: ...
@overload
def ensure_type(ty: Literal["time32[ms]"]) -> Time32Type[Literal["ms"]]: ...
@overload
def ensure_type(ty: Literal["time64[us]"]) -> Time64Type[Literal["us"]]: ...
@overload
def ensure_type(ty: Literal["time64[ns]"]) -> Time64Type[Literal["ns"]]: ...
@overload
def ensure_type(ty: Literal["timestamp[s]"]) -> TimestampType[Literal["s"], Any]: ...
@overload
def ensure_type(ty: Literal["timestamp[ms]"]) -> TimestampType[Literal["ms"], Any]: ...
@overload
def ensure_type(ty: Literal["timestamp[us]"]) -> TimestampType[Literal["us"], Any]: ...
@overload
def ensure_type(ty: Literal["timestamp[ns]"]) -> TimestampType[Literal["ns"], Any]: ...
@overload
def ensure_type(ty: Literal["duration[s]"]) -> DurationType[Literal["s"]]: ...
@overload
def ensure_type(ty: Literal["duration[ms]"]) -> DurationType[Literal["ms"]]: ...
@overload
def ensure_type(ty: Literal["duration[us]"]) -> DurationType[Literal["us"]]: ...
@overload
def ensure_type(ty: Literal["duration[ns]"]) -> DurationType[Literal["ns"]]: ...
@overload
def ensure_type(ty: Literal["month_day_nano_interval"]) -> MonthDayNanoIntervalType: ...
def schema(
    fields: Iterable[Field] | Iterable[tuple[str, DataType]] | Mapping[str, DataType],
    metadata: dict[bytes | str, bytes | str] | None = None,
) -> Schema: ...
def from_numpy_dtype(dtype: np.dtype) -> DataType: ...
def is_boolean_value(obj: Any) -> bool: ...
def is_integer_value(obj: Any) -> bool: ...
def is_float_value(obj: Any) -> bool: ...

__all__ = [
    "_Weakrefable",
    "_Metadata",
    "DataType",
    "_BasicDataType",
    "NullType",
    "BoolType",
    "Uint8Type",
    "Int8Type",
    "Uint16Type",
    "Int16Type",
    "Uint32Type",
    "Int32Type",
    "Uint64Type",
    "Int64Type",
    "Float16Type",
    "Float32Type",
    "Float64Type",
    "Date32Type",
    "Date64Type",
    "MonthDayNanoIntervalType",
    "StringType",
    "LargeStringType",
    "StringViewType",
    "BinaryType",
    "LargeBinaryType",
    "BinaryViewType",
    "TimestampType",
    "Time32Type",
    "Time64Type",
    "DurationType",
    "FixedSizeBinaryType",
    "Decimal128Type",
    "Decimal256Type",
    "ListType",
    "LargeListType",
    "ListViewType",
    "LargeListViewType",
    "FixedSizeListType",
    "DictionaryMemo",
    "DictionaryType",
    "MapType",
    "StructType",
    "UnionType",
    "SparseUnionType",
    "DenseUnionType",
    "RunEndEncodedType",
    "BaseExtensionType",
    "ExtensionType",
    "FixedShapeTensorType",
    "PyExtensionType",
    "UnknownExtensionType",
    "register_extension_type",
    "unregister_extension_type",
    "KeyValueMetadata",
    "ensure_metadata",
    "Field",
    "Schema",
    "unify_schemas",
    "field",
    "null",
    "bool_",
    "uint8",
    "int8",
    "uint16",
    "int16",
    "uint32",
    "int32",
    "int64",
    "uint64",
    "tzinfo_to_string",
    "string_to_tzinfo",
    "timestamp",
    "time32",
    "time64",
    "duration",
    "month_day_nano_interval",
    "date32",
    "date64",
    "float16",
    "float32",
    "float64",
    "decimal128",
    "decimal256",
    "string",
    "utf8",
    "binary",
    "large_binary",
    "large_string",
    "large_utf8",
    "binary_view",
    "string_view",
    "list_",
    "large_list",
    "list_view",
    "large_list_view",
    "map_",
    "dictionary",
    "struct",
    "sparse_union",
    "dense_union",
    "union",
    "run_end_encoded",
    "fixed_shape_tensor",
    "type_for_alias",
    "ensure_type",
    "schema",
    "from_numpy_dtype",
    "is_boolean_value",
    "is_integer_value",
    "is_float_value",
]
