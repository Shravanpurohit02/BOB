
from __future__ import annotations
from enum import Enum


class ExecutionMode(str, Enum):
    GENERATION = "generation"
    CHAT = "chat"
    ANALYSIS = "analysis"
