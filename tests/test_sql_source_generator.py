from firebird_mock.types import ProcedureParameter
from firebird_mock.sql_source_generator import SQLSourceGenerator


def test_select_procedure_statement():
    select_statement1 = SQLSourceGenerator.get_select_procedure_statement(
        name="PROCEDURE", parameters_count=1
    )
    assert select_statement1 == "select * from PROCEDURE(?)"

    select_statement5 = SQLSourceGenerator.get_select_procedure_statement(
        name="PROCEDURE", parameters_count=5
    )

    assert select_statement5 == "select * from PROCEDURE(?,?,?,?,?)"


def test_select_procedure_statement_named_params():
    named_parameters = {"param1": 1, "param2": None, "param4": "four"}

    input_parameters = [
        ProcedureParameter(name="param1", type_name="integer", type_length=4),
        ProcedureParameter(name="param2", type_name="integer", type_length=4),
        ProcedureParameter(name="param3", type_name="integer", type_length=4),
        ProcedureParameter(name="param4", type_name="varchar", type_length=4),
        ProcedureParameter(name="param5", type_name="integer", type_length=4),
    ]
    select_statement1 = SQLSourceGenerator.get_select_procedure_statement_named_params(
        name="PROCEDURE",
        named_parameters=named_parameters,
        input_parameters=input_parameters,
    )

    assert select_statement1 == "select * from PROCEDURE(1,null,null,'four',null)"
