# Pandera-Tool

Pandera-Tool is a package for [pandera](https://github.com/unionai-oss/pandera).

- DataFrame type definition
- Validation
- Type coerce

## Installation

```
pip install pandera-tool
```

## Example

### DataFrame type definition

```python
from io import StringIO
from typing import Tuple
import pandas as pd
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
```

### Validation

```python
@check_annotations
def func_ok(df: DataFrameIn) -> DataFrameOut:
    return df.assign(Age=2)

@check_annotations
def func_err(df: DataFrameIn) -> DataFrameOut:
    return df.assign(Age="")

@check_annotations
def func_err_output_tuple(df: DataFrameIn) -> Tuple[DataFrameOut]:
    return (df.assign(Age=""),)

df_ok = pd.DataFrame({"Name": ["1"]})
df_ng = pd.DataFrame({"Name": [1]})

func_ok(df_ok)  # OK

try:
    func_ok(df_ng)  # Input error
except SchemaError as e:
    print(e)

try:
    func_err(df_ok)  # Output error
except SchemaError as e:
    print(e)

try:
    func_err_output_tuple(df_ok)  # Output error
except SchemaError as e:
    print(e)
```

### Type coerce

```python
df1 = pd.read_csv(StringIO("Name\n1"))
try:
    func_ok(df1)  # Input error
except SchemaError as e:
    print(e)

df2 = pd.read_csv(StringIO("Name\n1"), dtype=dtype(DataFrameIn))
func_ok(df2)  # OK

df3 = df_ng.astype(dtype(DataFrameIn))
func_ok(df3)  # OK
```
