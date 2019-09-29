from functools import wraps
from typing import Callable, List, Any, Dict, Optional, Iterator

import fdb

from firebird_mock.types import ProcedureParameter


# pylint: disable=protected-access
def with_connection(method: Callable) -> Callable:
    @wraps(method)
    def with_connection_wrapper(
        self, *method_args: List[Any], **method_kwargs: Dict[str, Any]
    ) -> Any:
        if not self._cursor or not self._connection:
            self._connection = fdb.connect(
                dsn=self._dsn,
                user=self._user,
                password=self._password,
                charset=self._charset,
            )
            self._cursor = self._connection.cursor()
        result = method(self, *method_args, **method_kwargs)
        return result

    return with_connection_wrapper


# pylint: enable=protected-access


class Firebird:
    _cursor: Optional[fdb.Cursor] = None
    _connection: Optional[fdb.Connection] = None

    def __init__(
        self, dsn: str, user: str, password: str, charset: str = "UTF8"
    ) -> None:
        self._dsn = dsn
        self._user = user
        self._password = password
        self._charset = charset

    @with_connection
    def get_procedure_source(self, name: str) -> str:
        query = """
        select rdb$procedure_source from rdb$procedures where rdb$procedure_name = ?
        """
        result_cursor = self._cursor.execute(query, (name,))
        row = result_cursor.fetchone()

        return row[0]

    @with_connection
    def get_procedure_parameters(
        self, procedure_name: str, parameter_type: int
    ) -> Iterator[ProcedureParameter]:

        query = """
select pp.rdb$parameter_name, f.rdb$field_type, f.rdb$field_length
  from rdb$procedure_parameters as pp
       left join rdb$fields as f on pp.rdb$field_source = f.rdb$field_name
 where pp.rdb$procedure_name = ?
   and pp.rdb$parameter_type = ?
 order by rdb$parameter_number;
        """

        result_cursor = self._cursor.execute(query, (procedure_name, parameter_type))
        for row in result_cursor.iter():
            yield ProcedureParameter(*row)

    @with_connection
    def drop_procedure(self, procedure_name: str) -> None:
        self.execute_with_commit(f"DROP PROCEDURE {procedure_name}")

    @with_connection
    def execute_with_commit(self, query):
        self._cursor.execute(query)
        self._connection.commit()

    @with_connection
    def execute(self, query, params=None):
        # TODO: *params удобнее
        return self._cursor.execute(query, params)

    @with_connection
    def close_connection(self):
        self._connection.close()


def get_fb_exception_text(ex):
    return ex.args[0].split("\n- ")[4].encode("windows-1251").decode("utf-8")
