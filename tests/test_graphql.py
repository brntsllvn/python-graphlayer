from precisely import assert_that, has_attrs, is_mapping

import graphlayer as g
from graphlayer import schema
from graphlayer.graphql import document_text_to_query
from graphlayer.iterables import to_dict


def test_simple_query_is_converted_to_object_query():
    Root = g.ObjectType(
        "Root",
        (
            g.field("one", type=g.IntType),
        ),
    )
    
    graphql_query = """
        query {
            one
        }
    """
    
    object_query = document_text_to_query(graphql_query, query_type=Root)
    
    assert_that(object_query, is_query(
        Root(
            one=Root.one(),
        ),
    ))


def test_fields_can_have_alias():
    Root = g.ObjectType(
        "Root",
        (
            g.field("one", type=g.IntType),
        ),
    )
    
    graphql_query = """
        query {
            value: one
        }
    """
    
    object_query = document_text_to_query(graphql_query, query_type=Root)
    
    assert_that(object_query, is_query(
        Root(
            value=Root.one(),
        ),
    ))


def test_field_names_are_converted_to_snake_case():
    Root = g.ObjectType(
        "Root",
        (
            g.field("one_value", type=g.IntType),
        ),
    )
    
    graphql_query = """
        query {
            oneValue
        }
    """
    
    object_query = document_text_to_query(graphql_query, query_type=Root)
    
    assert_that(object_query, is_query(
        Root(
            oneValue=Root.one_value(),
        ),
    ))


def test_fields_can_be_nested():
    Root = g.ObjectType(
        "Root",
        fields=lambda: (
            g.field("one", type=One),
        ),
    )
    
    One = g.ObjectType(
        "One",
        fields=lambda: (
            g.field("two", type=Two),
        ),
    )
    
    Two = g.ObjectType(
        "Two",
        fields=lambda: (
            g.field("three", type=g.IntType),
        ),
    )
    
    graphql_query = """
        query {
            one {
                two {
                    three
                }
            }
        }
    """
    
    object_query = document_text_to_query(graphql_query, query_type=Root)
    
    assert_that(object_query, is_query(
        Root(
            one=Root.one(
                two=One.two(
                    three=Two.three(),
                ),
            ),
        ),
    ))


def is_query(query):
    if query == schema.scalar_query:
        return schema.scalar_query
    
    elif isinstance(query, schema.FieldQuery):
        return has_attrs(
            field=query.field,
            type_query=is_query(query.type_query),
        )
        
    elif isinstance(query, schema.ObjectQuery):
        return has_attrs(
            type=query.type,
            fields=is_mapping(to_dict(
                (name, is_query(field_query))
                for name, field_query in query.fields.items()
            )),
        )
        
    else:
        raise Exception("Unhandled query type: {}".format(type(query)))