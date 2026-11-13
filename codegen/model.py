"""Reads the schema, operations/ and behavior.json into a plain model that the
Go and C# emitters turn into code. Names match the Python SDK's:

- a fragment is a type with its own name (ProductFields)
- a selection inside a type is <Owner><Field> (StationFieldsWorkcenter)
- an operation's root field is <Operation>Result
- a selection that is only one fragment spread is that fragment's type
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from graphql import (
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    GraphQLEnumType,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLScalarType,
    ListTypeNode,
    NonNullTypeNode,
    OperationDefinitionNode,
    OperationType,
    SelectionSetNode,
    TypeNode,
    build_schema,
    parse,
    print_ast,
    validate,
)

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Ref:
    """A type as used somewhere: a named type, or a list, and whether it may be null."""

    kind: str  # "scalar", "enum", "input", "object" or "list"
    name: str = ""  # the scalar, enum, input or object (class) name
    of: Ref | None = None  # for a list
    nullable: bool = True


@dataclass
class Field:
    name: str  # as the API spells it
    ref: Ref
    description: str | None = None


@dataclass
class ObjectClass:
    name: str
    base: str | None
    """A fragment whose fields this one has too."""
    fields: list[Field]


@dataclass
class InputClass:
    name: str
    fields: list[Field]
    description: str | None


@dataclass
class Enum:
    name: str
    values: list[str]
    description: str | None


@dataclass
class Variable:
    name: str
    ref: Ref


@dataclass
class OperationModel:
    name: str
    root: str
    mutation: bool
    safe_to_repeat: bool
    document: str
    variables: list[Variable]
    result: Ref
    description: str | None
    page_node: Ref | None = None
    """For a list that pages: the type of one record."""


@dataclass
class Model:
    version: str
    retry: dict[str, int]
    enums: list[Enum]
    inputs: list[InputClass]
    classes: list[ObjectClass] = field(default_factory=list)
    operations: list[OperationModel] = field(default_factory=list)


def pascal(name: str) -> str:
    return name[0].upper() + name[1:]


def load() -> Model:
    schema = build_schema((ROOT / "schema" / "developer-api.graphql").read_text())
    document = parse("\n".join(p.read_text() for p in sorted((ROOT / "operations").glob("*.graphql"))))
    behavior = json.loads((ROOT / "behavior.json").read_text())
    problems = validate(schema, document)
    if problems:
        sys.exit("operations/ has problems:\n- " + "\n- ".join(p.message for p in problems))

    fragments: dict[str, FragmentDefinitionNode] = {}
    operations: list[OperationDefinitionNode] = []
    for definition in document.definitions:
        if isinstance(definition, FragmentDefinitionNode):
            fragments[definition.name.value] = definition
        elif isinstance(definition, OperationDefinitionNode):
            operations.append(definition)

    model = Model(
        version=(ROOT / "VERSION").read_text().strip(),
        retry=behavior["retry"],
        enums=[
            Enum(t.name, list(t.values), t.description)
            for t in sorted(schema.type_map.values(), key=lambda t: t.name)
            if isinstance(t, GraphQLEnumType) and not t.name.startswith("__")
        ],
        inputs=[],
    )

    def named(graphql_type):
        while isinstance(graphql_type, (GraphQLNonNull, GraphQLList)):
            graphql_type = graphql_type.of_type
        return graphql_type

    def wrap(graphql_type, inner: Ref) -> Ref:
        nullable = not isinstance(graphql_type, GraphQLNonNull)
        if not nullable:
            graphql_type = graphql_type.of_type
        if isinstance(graphql_type, GraphQLList):
            return Ref("list", of=wrap(graphql_type.of_type, inner), nullable=nullable)
        return Ref(inner.kind, inner.name, nullable=nullable)

    def parts(selection_set: SelectionSetNode) -> tuple[list[str], list[FieldNode]]:
        spreads, fields = [], []
        for selection in selection_set.selections:
            if isinstance(selection, FragmentSpreadNode):
                spreads.append(selection.name.value)
            elif isinstance(selection, FieldNode):
                fields.append(selection)
            else:
                sys.exit("Inline fragments aren't supported; use a named fragment")
        return spreads, fields

    def object_class(name: str, parent: GraphQLObjectType, selection_set: SelectionSetNode) -> str:
        spreads, fields = parts(selection_set)
        if len(spreads) == 1 and not fields:
            return spreads[0]
        if len(spreads) > 1:
            sys.exit(f"{name}: at most one fragment spread next to other fields (C# and Go have one base)")
        model.classes.append(
            ObjectClass(name, spreads[0] if spreads else None, [selection(name, parent, f) for f in fields])
        )
        return name

    def selection(owner: str, parent: GraphQLObjectType, node: FieldNode, class_name: str | None = None) -> Field:
        definition = parent.fields[node.name.value]
        inner_type = named(definition.type)
        if isinstance(inner_type, GraphQLObjectType):
            assert node.selection_set
            inner = Ref("object", object_class(class_name or owner + pascal(node.name.value), inner_type, node.selection_set))
        elif isinstance(inner_type, GraphQLEnumType):
            inner = Ref("enum", inner_type.name)
        else:
            inner = Ref("scalar", inner_type.name)
        return Field(node.name.value, wrap(definition.type, inner), definition.description)

    # Fragments, each after the fragments it uses.
    done: list[str] = []

    def spreads_in(selection_set: SelectionSetNode | None) -> list[str]:
        found: list[str] = []
        for s in selection_set.selections if selection_set else []:
            if isinstance(s, FragmentSpreadNode):
                found.append(s.name.value)
            elif isinstance(s, FieldNode):
                found.extend(spreads_in(s.selection_set))
        return found

    def visit(name: str) -> None:
        if name in done:
            return
        for spread in spreads_in(fragments[name].selection_set):
            visit(spread)
        done.append(name)
        fragment = fragments[name]
        parent = schema.get_type(fragment.type_condition.name.value)
        assert isinstance(parent, GraphQLObjectType)
        spreads, fields = parts(fragment.selection_set)
        if len(spreads) > 1:
            sys.exit(f"{name}: at most one fragment spread")
        model.classes.append(
            ObjectClass(name, spreads[0] if spreads else None, [selection(name, parent, f) for f in fields])
        )

    for name in fragments:
        visit(name)

    def input_ref(graphql_type) -> Ref:
        inner_type = named(graphql_type)
        kind = (
            "scalar"
            if isinstance(inner_type, GraphQLScalarType)
            else "enum"
            if isinstance(inner_type, GraphQLEnumType)
            else "input"
        )
        return wrap(graphql_type, Ref(kind, inner_type.name))

    model.inputs = [
        InputClass(t.name, [Field(n, input_ref(f.type), f.description) for n, f in t.fields.items()], t.description)
        for t in sorted(schema.type_map.values(), key=lambda t: t.name)
        if isinstance(t, GraphQLInputObjectType)
    ]

    def variable_ref(node: TypeNode) -> Ref:
        nullable = not isinstance(node, NonNullTypeNode)
        if not nullable:
            node = node.type  # type: ignore[attr-defined]
        if isinstance(node, ListTypeNode):
            return Ref("list", of=variable_ref(node.type), nullable=nullable)
        graphql_type = schema.get_type(node.name.value)  # type: ignore[attr-defined]
        return Ref(input_ref(graphql_type).kind, graphql_type.name, nullable=nullable)

    def used(selection_set: SelectionSetNode, found: list[str]) -> list[str]:
        for s in selection_set.selections:
            if isinstance(s, FragmentSpreadNode):
                if s.name.value not in found:
                    found.append(s.name.value)
                    used(fragments[s.name.value].selection_set, found)
            elif isinstance(s, FieldNode) and s.selection_set:
                used(s.selection_set, found)
        return found

    for operation in operations:
        name = operation.name.value  # type: ignore[union-attr]
        mutation = operation.operation == OperationType.MUTATION
        root_type = schema.mutation_type if mutation else schema.query_type
        assert root_type
        root_node = operation.selection_set.selections[0]
        assert isinstance(root_node, FieldNode)
        result = selection(name, root_type, root_node, class_name=f"{name}Result")
        text = "\n\n".join(
            print_ast(d) for d in [operation, *(fragments[f] for f in used(operation.selection_set, []))]
        )
        variables = [
            Variable(v.variable.name.value, variable_ref(v.type)) for v in operation.variable_definitions or []
        ]
        op = OperationModel(
            name=name,
            root=root_node.name.value,
            mutation=mutation,
            safe_to_repeat=(not mutation) or name in behavior["safeToRepeat"],
            document=text,
            variables=variables,
            result=result.ref,
            description=root_type.fields[root_node.name.value].description,
        )
        connection = named(root_type.fields[root_node.name.value].type)
        if (
            not mutation
            and name.startswith("List")
            and isinstance(connection, GraphQLObjectType)
            and {"nodes", "pageInfo"} <= set(connection.fields)
            and any(v.name == "after" for v in variables)
        ):
            result_class = next(c for c in model.classes if c.name == result.ref.name)
            nodes = next(f for f in result_class.fields if f.name == "nodes")
            assert nodes.ref.of
            op.page_node = nodes.ref.of
        model.operations.append(op)
    return model
