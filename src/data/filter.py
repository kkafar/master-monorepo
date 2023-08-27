import polars as pl
from .model import Col


def filter_sid(sid: int) -> pl.Expr:
    return pl.col(Col.SID) == sid

