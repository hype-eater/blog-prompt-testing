import typer
from langchain import OpenAI, PromptTemplate
from enum import Enum
import types
from typing import Callable
from RestrictedPython import compile_restricted, PrintCollector, safe_builtins
from RestrictedPython.Guards import guarded_unpack_sequence
from RestrictedPython.Eval import default_guarded_getiter

class LlmProvider(str, Enum):
    OPENAI = 'openai'
    HF_HUB = 'hfhub'
    HIYA = 'hiya'


class EmbeddingsProvider(str, Enum):
    OPENAI = 'openai'
    HUGGINGFACE = 'hf'


app = typer.Typer()
state = {
    "model_name": None,
    "provider": LlmProvider.HIYA,
    "embed_model": None,
    "embed_provider": EmbeddingsProvider.HUGGINGFACE,
}

@app.callback()
def main(model: str = None,
         provider: LlmProvider = LlmProvider.HIYA,
         embed_model: str = None,
         embed_provider: EmbeddingsProvider = EmbeddingsProvider.HUGGINGFACE,
         ):
    """A helpful and friendly CLI"""
    if model is not None:
        state["model_name"] = model
    if provider is not None:
        state["provider"] = provider
    if embed_model is not None:
        state["embed_model"] = embed_model
    if embed_provider is not None:
        state["embed_provider"] = embed_provider

GREETING_PROMPT = "An amusing greeting: "
INTRODUCTION_PROMPT_TMPL = PromptTemplate(
    input_variables=["name"],
    template="Hello, please call me {name}. A friendly greeting: ",
)


@app.command()
def hello():
    """Say hello"""
    executor = get_prompt_executor(**state)
    response = executor(GREETING_PROMPT)
    print(response.strip())


@app.command()
def intro(name: str = "User"):
    """Reply to an introduction"""
    executor = get_prompt_executor(**state)
    prompt = INTRODUCTION_PROMPT_TMPL.format_prompt(name=name)
    response = executor(prompt.to_string())
    print(response.strip())


@app.command()
def code(description: str = "a function that returns 'Hello, World!'"):
    """Generate Python code"""
    from prompts import PYTHON_FUNCTION_PROMPT_TMPL
    executor = get_prompt_executor(**state)
    prompt = PYTHON_FUNCTION_PROMPT_TMPL.format_prompt(description=description)
    response = executor(prompt.to_string())

    try:
        formatted_code = format_code(response)
        f = exec_code_and_return_function(formatted_code)
        if not f:
            print("** Not a function :(")
        print(formatted_code)
    except Exception:
        print("** OUCH! Unable to validate code:")
        print(response.strip())


@app.command()
def empty(query: str = "Hello!"):
    """Pass query through empty index"""
    service_context = create_service_context(**state)
    from query_engines import get_empty_index_query_engine
    query_engine = get_empty_index_query_engine(service_context)
    response = query_engine.query(query)
    print(response)


@app.command()
def city_df(query: str = "What is the largest city?"):
    """Query over city stats data frame"""
    from query_engines import create_city_stats_df, get_df_query_engine
    service_context = create_service_context(**state)
    df = create_city_stats_df()
    query_engine = get_df_query_engine(service_context, df=df)
    response = query_engine.query(query)
    print(response.response)


@app.command()
def city_db(query: str = "What is the largest city?"):
    """Query over city stats database"""
    from query_engines import create_and_populate_city_stats_db, get_db_query_engine
    service_context = create_service_context(**state)
    db = create_and_populate_city_stats_db()
    query_engine = get_db_query_engine(service_context, sql_database=db)
    response = query_engine.query(query)
    print(response.response)


def get_prompt_executor(model_name="gpt-3.5-turbo", provider="openai"):
    match provider:
        case "hfhub":
            model_name = model_name or "google/flan-t5-xxl"
            from langchain import HuggingFaceHub
            executor = HuggingFaceHub(repo_id=model_name)
        case "hiya":
            from hiya import Hiya
            executor = Hiya()
        case _:  # default to "openai"
            model_name = model_name or "gpt-3.5-turbo"
            executor = OpenAI(model_name=model_name)
    return executor


def format_code(raw_str: str) -> str:
    from black import format_str, FileMode
    formatted_code_str = format_str(raw_str, mode=FileMode())
    return formatted_code_str


def exec_code_and_return_function(code_str: str) -> Callable:
    restricted_code = compile_restricted(code_str, '<string>', 'exec')
    restricted_globals = {
        "__builtins__": safe_builtins,
        "_print_": PrintCollector,
        "_unpack_sequence_": guarded_unpack_sequence,
        "_getiter_": default_guarded_getiter,
    }

    orig_global_keys = set(restricted_globals.keys())

    exec(restricted_code, restricted_globals)

    new_funs = [f for k, f in restricted_globals.items() if isinstance(f, types.FunctionType) and k not in orig_global_keys]
    return new_funs[0] if new_funs else None

from enum import Enum


def get_embedding(model_name, provider=EmbeddingsProvider.OPENAI):
    match provider:
        case EmbeddingsProvider.HUGGINGFACE:
            from llama_index import LangchainEmbedding
            from langchain.embeddings import HuggingFaceEmbeddings
            model_name = model_name or "sentence-transformers/multi-qa-mpnet-base-dot-v1"
            embedding = LangchainEmbedding(HuggingFaceEmbeddings(model_name=model_name,
                                                                 model_kwargs={
                                                                     'device': 'cpu'}))
        case _:  # default to "openai"
            from llama_index.embeddings.openai import OpenAIEmbeddingModelType
            from llama_index import OpenAIEmbedding
            model_name = model_name or OpenAIEmbeddingModelType.TEXT_EMBED_ADA_002
            embedding = OpenAIEmbedding(model=model_name)
    return embedding

def create_service_context(model_name=None,
                           embed_model=None,
                           provider=LlmProvider.OPENAI,
                           embed_provider=EmbeddingsProvider.HUGGINGFACE):

    from llama_index import ServiceContext
    llm = get_prompt_executor(model_name, provider)
    embed_model = get_embedding(embed_model, embed_provider)
    service_context = ServiceContext.from_defaults(llm=llm,
                                                   embed_model=embed_model,
                                                   callback_manager=None,
                                                   )

    return service_context

if __name__ == '__main__':
    app()