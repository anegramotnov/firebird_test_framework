from functools import partial
from typing import Optional, List

from firebird_mock.firebird import Firebird
from firebird_mock.procedures import StoredProcedure


class procedure_mock:  # pylint: disable=invalid-name
    procedure_under_test: Optional[StoredProcedure] = None
    original_procedure: Optional[StoredProcedure] = None
    mock_procedure: Optional[StoredProcedure] = None

    def __init__(
        self,
        firebird: Firebird,
        procedure_under_test: str,
        procedure: str,
        return_values: List,
    ):
        self._firebird = firebird
        self._ut_procedure_name = procedure_under_test
        self._mock_procedure_name = procedure
        self._return_values = return_values

    @classmethod
    def factory(cls, firebird: Firebird, procedure_under_test: str):
        return partial(cls, firebird, procedure_under_test)

    def __enter__(self):
        self.procedure_under_test = StoredProcedure(
            firebird=self._firebird, name=self._ut_procedure_name
        )
        self.original_procedure = StoredProcedure(
            firebird=self._firebird, name=self._mock_procedure_name
        )

        self.mock_procedure = self.original_procedure.get_mock(
            return_values=self._return_values
        )

        self.mock_procedure.recompile()
        self.procedure_under_test.recompile()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.original_procedure.recompile()
        self.procedure_under_test.recompile()
