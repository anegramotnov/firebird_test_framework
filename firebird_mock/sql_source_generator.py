from typing import Dict, List, Union
from firebird_mock.types import ProcedureParameter


class SQLSourceGenerator:
    # TODO: вывести побольше дебаг-информации в комментарии процедуры
    CREATE_OR_ALTER_PROCEDURE_TEMPLATE = """
    create or alter procedure {name} (
        {input_parameters}
    )
    returns (
        {output_parameters}
    )
    as
    -- autogenerated from procedures_test_mock
    {source}
    """

    PROCEDURE_SOURCE_TEMPLATE = """
    begin
        -- autogenerated from procedures_test_mock
        {return_values}
        suspend;
    end
    """

    PARAMS_TEMPLATE = (",\n", "{name} {type_name}")

    RETURN_VALUES_TEMPLATE = ("\n", "{name} = {value};")

    SELECT_PROCEDURE_STATEMENT_TEMPLATE = "select * from {name}({parameters})"

    PARAM_TYPE_MAP = {
        8: "integer",
        10: "float",
        14: "char",
        27: "double precision",
        37: "varchar({type_length})",
    }

    PARAM_STRINGIFY_MAP = {"integer": str, "varchar": lambda p: f"'{p}'"}

    @classmethod
    def get_recompile_statement(
        cls,
        name: str,
        source: str,
        input_parameters: List[ProcedureParameter],
        output_parameters: List[ProcedureParameter],
    ) -> str:
        input_parameters_source = cls.PARAMS_TEMPLATE[0].join(
            (
                cls.PARAMS_TEMPLATE[1].format(
                    name=ip.name,
                    type_name=cls.PARAM_TYPE_MAP[ip.type_name].format(
                        type_length=ip.type_length
                    ),
                )
                for ip in input_parameters
            )
        )

        output_parameters_source = cls.PARAMS_TEMPLATE[0].join(
            (
                cls.PARAMS_TEMPLATE[1].format(
                    name=op.name,
                    type_name=cls.PARAM_TYPE_MAP[op.type_name].format(
                        type_length=op.type_length
                    ),
                )
                for op in output_parameters
            )
        )

        create_procedure_statement = cls.CREATE_OR_ALTER_PROCEDURE_TEMPLATE.format(
            name=name,
            source=source,
            input_parameters=input_parameters_source,
            output_parameters=output_parameters_source,
        )
        return create_procedure_statement

    @classmethod
    def get_stringify_parameter(
        cls, parameter_type: str, parameter_value: Union[str, int]
    ):
        if parameter_value is not None:
            return cls.PARAM_STRINGIFY_MAP[parameter_type](parameter_value)
        else:
            return "null"

    @classmethod
    def get_select_procedure_statement(cls, name, parameters_count) -> str:
        parameters = ",".join("?" * parameters_count)
        return cls.SELECT_PROCEDURE_STATEMENT_TEMPLATE.format(
            name=name, parameters=parameters
        )

    @classmethod
    def get_select_procedure_statement_named_params(
        cls,
        name: str,
        input_parameters: List[ProcedureParameter],
        named_parameters: Dict,
    ) -> str:

        parameters_with_null = (
            cls.get_stringify_parameter(
                param.type_name, named_parameters.get(param.name)
            )
            for param in input_parameters
        )

        parameters = ",".join(parameters_with_null)

        return cls.SELECT_PROCEDURE_STATEMENT_TEMPLATE.format(
            name=name, parameters=parameters
        )

    @classmethod
    def get_source_by_return_values(cls, return_values: Dict[str, str]) -> str:
        return_values_source = cls.RETURN_VALUES_TEMPLATE[0].join(
            (
                cls.RETURN_VALUES_TEMPLATE[1].format(name=rv[0], value=rv[1])
                for rv in return_values.items()
            )
        )
        return cls.PROCEDURE_SOURCE_TEMPLATE.format(return_values=return_values_source)
