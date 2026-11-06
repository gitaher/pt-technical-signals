"""Structured tool and task contracts; declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    COMPUTE = "compute"


class Task(Enum):
    RUN = "derive-signals"


@dataclass
class Bar(Output):
    date: Annotated[str, "Trading session YYYY-MM-DD"]
    close: Annotated[float, "Positive adjusted closing price"]


@dataclass
class TaskInput(Output):
    bars: Annotated[list[Bar], "Strictly chronological unique daily bars"]
    cutoff: Annotated[str, "Latest permitted session YYYY-MM-DD, inclusive"]
    short_window: Annotated[int, "Short SMA length, at least one"]
    long_window: Annotated[int, "Long SMA length, greater than short"]
    rsi_period: Annotated[int, "Number of differences in simple RSI"]


@dataclass
class TaskOutput(Output):
    sma_short: Annotated[float, "Arithmetic mean over the last short_window closes"]
    sma_long: Annotated[float, "Arithmetic mean over the last long_window closes"]
    rsi: Annotated[float, "100*gains/(gains+losses); flat prices yield 50"]
    signal: Annotated[str, "buy if close>short>long; sell if close<short<long; otherwise hold"]


TOOLS = {Tool.COMPUTE: (TaskInput, TaskOutput)}
TASKS = {Task.RUN: (TaskInput, TaskOutput)}
