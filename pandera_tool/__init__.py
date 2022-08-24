from pandera import SchemaModel, check_io, check_types
from pandera.typing import DataFrame


def to_dataframe(schema):
    return DataFrame[schema]


def to_schema(df_type):
    return df_type.__args__[0]


def check_annotations(func):
    anr = func.__annotations__.get("return")
    if anr and getattr(anr, "__origin__") == tuple:
        out = []
        for i, typ in enumerate(anr.__args__):
            tydf = getattr(typ, "__args__", (type,))[0]
            if issubclass(tydf, SchemaModel):
                out.append((i, to_schema(typ)))
        if out:
            return check_io(out=out)(check_types(func))
    return check_types(func)


def dtype(df_type, use_nullable=True):
    dc = {}
    schema = to_schema(df_type).to_schema()
    for name, column in schema.columns.items():
        typ = column.dtype.type
        if use_nullable and column.nullable and column.dtype.type == int:
            typ = "Int64"
        dc[name] = typ
    return dc
