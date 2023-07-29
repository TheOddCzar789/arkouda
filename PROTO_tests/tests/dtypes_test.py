import numpy as np
import pytest

import arkouda as ak
from arkouda import dtypes

"""
DtypesTest encapsulates arkouda dtypes module methods
"""

SUPPORTED_NP_DTYPES = [
    bool,
    int,
    float,
    str,
    np.bool_,
    np.int64,
    np.float64,
    np.uint8,
    np.uint64,
    np.str_,
]


class TestDTypes:
    @pytest.mark.parametrize("dtype", SUPPORTED_NP_DTYPES)
    def test_check_np_dtype(self, dtype):
        dtypes.check_np_dtype(np.dtype(dtype))

        with pytest.raises(TypeError):
            dtypes.check_np_dtype(np.dtype(np.int16))
        with pytest.raises(TypeError):
            dtypes.check_np_dtype("np.str")
        with pytest.raises(TypeError):
            dtypes.check_np_dtype("bigint")

    def test_translate_np_dtype(self):
        for b in [np.bool_, bool]:
            assert ("bool", 1) == dtypes.translate_np_dtype(np.dtype(b))

        for s in [np.str_, str]:
            assert ("str", 0) == dtypes.translate_np_dtype(np.dtype(s))

        assert ("int", 8) == dtypes.translate_np_dtype(np.dtype(np.int64))
        assert ("uint", 8) == dtypes.translate_np_dtype(np.dtype(np.uint64))
        assert ("float", 8) == dtypes.translate_np_dtype(np.dtype(np.float64))
        assert ("uint", 1) == dtypes.translate_np_dtype(np.dtype(np.uint8))

    def test_resolve_scalar_dtype(self):
        assert "bool" == dtype.resolve_scalar_dtype(True)
        assert "int64" == dtype.resolve_scalar_dtype(1)
        assert "int64" == dtype.resolve_scalar_dtype(-1)
        assert "int64" == dtype.resolve_scalar_dtype(np.int64(1))
        assert "float64" == dtype.resolve_scalar_dtype(float(0.0))
        assert "float64" == dtype.resolve_scalar_dtype(float(-1.0))
        assert "float64" == dtype.resolve_scalar_dtype(np.nan)
        assert "float64" == dtype.resolve_scalar_dtype(np.inf)
        assert "float64" == dtype.resolve_scalar_dtype(-np.inf)
        assert "str" == dtype.resolve_scalar_dtype("test")
        assert "<class 'list'>" == dtype.resolve_scalar_dtype([1])
        assert "uint64" == dtype.resolve_scalar_dtype(2 ** 63 + 1)
        assert "bigint" == dtype.resolve_scalar_dtype(2 ** 64)

    @pytest.mark.parametrize("size", pytest.prob_size)
    def test_pdarrays_datatypes(self, size):
        assert dtypes.dtype("int64") == ak.array(np.arange(size)).dtype
        assert dtypes.dtype("uint64") == ak.array(np.arange(size), ak.uint64).dtype
        assert dtypes.dtype("bool") == ak.ones(size, ak.bool).dtype
        assert dtypes.dtype("float64") == ak.ones(size).dtype
        assert dtypes.dtype("str") == ak.array([f"string {i}" for i in range(size)]).dtype
        assert dtypes.dtype("bigint") == ak.bigint_from_uint_arrays([ak.ones(size, dtype=ak.uint64), ak.arange(size, dtype=ak.uint64)]).dtype
        assert dtypes.dtype("bigint") == ak.array([i for i in range(2**200, 2**200 + size)]).dtype

    @pytest.mark.parametrize("supported", [1, np.int64(1), np.int64(1.0), 1, np.uint32(1)])
    @pytest.mark.parametrize("unsupported", [1.0, "1"])
    def test_isSupportedInt(self, supported, unsupported):
        assert dtypes.isSupportedInt(supported)
        assert not dtypes.isSupportedInt(unsupported)

    @pytest.mark.parametrize("supported", [1.0, float(1), np.float64(1), np.float64(1.0)])
    @pytest.mark.parametrize("unsupported", [np.int64(1.0), int(1.0), "1.0"])
    def test_isSupportedFloat(self, supported, unsupported):
        assert dtypes.isSupportedFloat(supported)
        assert not dtypes.isSupportedFloat(unsupported)

    @pytest.mark.parametrize(
        "dtype, val",
        [
            ("bool", dtypes.DType.BOOL),
            ("float", dtypes.DType.FLOAT),
            ("float64", dtypes.DType.FLOAT64),
            ("int", dtypes.DType.INT),
            ("int64", dtypes.DType.INT64),
            ("str", dtypes.DType.STR),
            ("uint8", dtypes.DType.UINT8),
            ("bigint", dtypes.DType.BIGINT),
        ],
    )
    def test_DtypeEnum(self, dtype, val):
        assert dtype == str(val)

        enum_vals = frozenset(
            {"float", "float64", "bool", "uint8", "int", "int64", "str", "uint64", "bigint"}
        )
        assert enum_vals == ak.DTypes
        assert enum_vals == ak.ARKOUDA_SUPPORTED_DTYPES

    def test_NumericDTypes(self):
        num_types = frozenset(["bool", "float", "float64", "int", "int64", "uint64", "bigint"])
        assert num_types == dtypes.NumericDTypes

    @pytest.mark.parametrize(
        "dtype, val",
        [
            (np.str_, "string"),
            (np.str_, "<class 'str'>"),
            (np.int64, "int64"),
            (np.int64, "<class 'numpy.int64'>"),
            (np.float64, "float64"),
            (np.float64, "<class 'numpy.float64'>"),
            (np.bool_, "bool"),
            (np.dtype(bool), "bool"),
            (np.bool_, "<class 'bool'>"),
            (np.dtype(bool), "<class 'bool'>"),
            (np.int64, "datetime64[ns]"),
            (np.int64, "timedelta64[ns]"),
        ],
    )
    def test_SeriesDTypes(self, dtype, val):
        assert dtype == dtypes.SeriesDTypes[val]

    def test_scalars(self):
        assert "typing.Union[bool, numpy.bool_]" == str(ak.bool_scalars)
        assert "typing.Union[float, numpy.float64]" == str(ak.float_scalars)
        assert (
            "typing.Union[int, numpy.int8, numpy.int16, numpy.int32, numpy.int64, "
            + "numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64]"
        ) == str(ak.int_scalars)
        assert (
            "typing.Union[float, numpy.float64, int, numpy.int8, numpy.int16, numpy.int32, "
            + "numpy.int64, numpy.uint8, numpy.uint16, numpy.uint32, numpy.uint64]"
        ) == str(ak.numeric_scalars)
        assert "typing.Union[str, numpy.str_]", str(ak.str_scalars)
        assert (
            "typing.Union[numpy.float64, numpy.int8, numpy.int16, numpy.int32, "
            + "numpy.int64, numpy.bool_, numpy.str_, numpy.uint8, numpy.uint16, numpy.uint32, "
            + "numpy.uint64]"
        ) == str(ak.numpy_scalars)
        assert (
            "typing.Union[bool, numpy.bool_, float, numpy.float64, int, numpy.int8, "
            + "numpy.int16, numpy.int32, numpy.int64, numpy.uint8, numpy.uint16, numpy.uint32,"
            + " numpy.uint64, numpy.str_, str]"
        ) == str(ak.all_scalars)

    @pytest.mark.parametrize(
        "type_format, dtype",
        [
            ("{}", "bool"),
            ("{:n}", "int64"),
            ("{:.17f}", "float64"),
            ("{:n}", "uint8"),
            ("f", "np.float64"),
            ("{:n}", "uint64"),
            ("{:n}", "bigint"),
        ],
    )
    def test_number_format_strings(self, type_format, dtype):
        assert dtypes.NUMBER_FORMAT_STRINGS[dtype] == type_format
