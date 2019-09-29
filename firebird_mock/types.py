from __future__ import annotations

import enum
from typing import List, NamedTuple


class ParameterTypes(enum.Enum):
    INPUT = 0
    OUTPUT = 1


class ProcedureParameter(NamedTuple):
    name: str
    type_name: str
    type_length: int


class ProcedureMetadata(NamedTuple):
    source: str
    input_parameters: List[ProcedureParameter]
    output_parameters: List[ProcedureParameter]
