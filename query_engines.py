from llama_index import EmptyIndex, PromptTemplate, prompts

def get_empty_index_query_engine(service_context, template=None):
    template = template or "{query_str}"
    simple_template = PromptTemplate(template, prompt_type=prompts.PromptType.SIMPLE_INPUT)
    query_engine = EmptyIndex(service_context=service_context) \
        .as_query_engine(simple_template=simple_template)
    return query_engine

from llama_index.query_engine import PandasQueryEngine
import pandas as pd


def create_city_stats_df():
    rows = [
        {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
        {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
        {"city_name": "Chicago", "population": 2679000, "country": "United States"},
        {"city_name": "Seoul", "population": 9776000, "country": "South Korea"},
    ]
    df = pd.DataFrame(rows)

    return df


def get_df_query_engine(service_context, df):
    query_engine = PandasQueryEngine(
        service_context=service_context,
        df=df,
    )
    return query_engine


def create_and_populate_city_stats_db():
    from sqlalchemy import create_engine
    from llama_index import SQLDatabase

    engine = create_engine("sqlite:///:memory:")

    df = create_city_stats_df()
    table_name = 'city_stats'

    with engine.begin() as connection:
        df.to_sql(name=table_name, con=connection, if_exists='append')

    tables = [table_name]
    db = SQLDatabase(engine, include_tables=tables)

    return db


def get_db_query_engine(service_context, sql_database):
    from llama_index.indices.struct_store import NLSQLTableQueryEngine
    query_engine = NLSQLTableQueryEngine(
        service_context=service_context,
        sql_database=sql_database
    )
    return query_engine

