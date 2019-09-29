from __future__ import annotations

import hashlib
import time
from typing import Optional
from functools import partial

from firebird_mock.firebird import Firebird
from firebird_mock.sql_source_generator import SQLSourceGenerator
from firebird_mock.types import ProcedureMetadata, ParameterTypes


class StoredProcedure:
    name: str
    metadata: Optional[ProcedureMetadata] = None
    firebird: Optional[Firebird]  # pylint: disable=used-before-assignment
    sql_source_generator = SQLSourceGenerator

    def __init__(self, firebird: Firebird, name: str):
        self.name = name.upper()
        self.firebird = firebird

    @classmethod
    def factory(cls, firebird: Firebird):
        return partial(cls, firebird)

    def _get_stash_name(self):
        timestamp = int(time.time())
        name_hash = hashlib.md5(self.name.encode("ascii")).hexdigest()[:12].upper()
        # TODO: могут быть коллизии
        stash_name = f"STASHED_{timestamp}_{name_hash}"
        return stash_name

    def get_mock(self, return_values) -> StoredProcedure:
        mock_procedure = StoredProcedure(firebird=self.firebird, name=self.name)

        mock_source = self.sql_source_generator.get_source_by_return_values(
            return_values=return_values
        )
        mock_procedure.metadata = self._get_metadata_from_db()._replace(
            source=mock_source
        )
        return mock_procedure

    def get_stash(self) -> StoredProcedure:
        stash_name = self._get_stash_name()

        stash_procedure = StoredProcedure(firebird=self.firebird, name=stash_name)
        stash_procedure.metadata = self.metadata

        return stash_procedure

    def drop(self) -> None:
        self.firebird.drop_procedure(self.name)

    def _get_metadata_from_db(self) -> ProcedureMetadata:
        if self.metadata is None:
            input_parameters = [
                p
                for p in self.firebird.get_procedure_parameters(
                    self.name, ParameterTypes.INPUT.value
                )
            ]
            output_parameters = [
                p
                for p in self.firebird.get_procedure_parameters(
                    self.name, ParameterTypes.OUTPUT.value
                )
            ]
            self.metadata = ProcedureMetadata(
                source=self.firebird.get_procedure_source(self.name),
                input_parameters=input_parameters,
                output_parameters=output_parameters,
            )
        return self.metadata

    def execute(self, *args, **kwargs):
        metadata = self._get_metadata_from_db()
        if kwargs:

            select_statement = self.sql_source_generator.get_select_procedure_statement_named_params(
                name=self.name,
                input_parameters=metadata.input_parameters,
                named_parameters=kwargs,
            )
            return self.firebird.execute(select_statement)
        else:
            select_statement = self.sql_source_generator.get_select_procedure_statement(
                self.name, len(metadata.input_parameters)
            )
            return self.firebird.execute(select_statement, args)

    def recompile(self) -> None:
        metadata = self._get_metadata_from_db()
        recompile_statement = self.sql_source_generator.get_recompile_statement(
            name=self.name,
            source=metadata.source,
            input_parameters=metadata.input_parameters,
            output_parameters=metadata.output_parameters,
        )
        self.firebird.execute_with_commit(recompile_statement)
