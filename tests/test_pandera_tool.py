from io import StringIO
from typing import Tuple

import pandas as pd
import pytest
from pandera import Field, SchemaModel
from pandera.errors import SchemaError
from pandera.typing import Series
from pandera_tool import check_annotations, dtype, to_dataframe, to_schema


@to_dataframe
class DataFrameIn(SchemaModel):
    Name: Series[str] = Field()

    class Config:
        strict = True


@to_dataframe
class DataFrameOut(to_schema(DataFrameIn)):
    Age: Series[int] = Field()

    class Config:
        strict = True


@check_annotations
def func_ok(df: DataFrameIn) -> DataFrameOut:
    return df.assign(Age=2)


@check_annotations
def func_err(df: DataFrameIn) -> DataFrameOut:
    return df.assign(Age="")


@check_annotations
def func_err_output_tuple(df: DataFrameIn) -> Tuple[DataFrameOut]:
    return (df.assign(Age=""),)


@pytest.fixture()
def df_ok():
    return pd.DataFrame({"Name": ["1"]})


@pytest.fixture()
def df_ng():
    return pd.DataFrame({"Name": [1]})


def test_ok(df_ok):
    func_ok(df_ok)  # OK


def test_ng_input_err(df_ng):
    with pytest.raises(SchemaError):
        func_ok(df_ng)  # Input error


def test_ng_output_err(df_ok):
    with pytest.raises(SchemaError):
        func_err(df_ok)  # Output error


def test_ng_output_tuple(df_ok):
    with pytest.raises(SchemaError):
        func_err_output_tuple(df_ok)  # Output error


def test_read_csv():
    df1 = pd.read_csv(StringIO("Name\n1"))
    with pytest.raises(SchemaError):
        func_ok(df1)  # Input error
    df2 = pd.read_csv(StringIO("Name\n1"), dtype=dtype(DataFrameIn))
    func_ok(df2)  # OK


def test_coerce(df_ng):
    func_ok(df_ng.astype(dtype(DataFrameIn)))  # OK
