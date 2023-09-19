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


app = typer.Typer()
state = {
    "model_name": None,
    "provider": LlmProvider.HIYA
}


@app.callback()
def main(model: str = None, provider: LlmProvider = LlmProvider.HIYA):
    """A helpful and friendly CLI"""
    if model is not None:
        state["model_name"] = model
    if provider is not None:
        state["provider"] = provider


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


def get_prompt_executor(model_name="text-davinci-003", provider="openai"):
    match provider:
        case "hfhub":
            model_name = model_name or "google/flan-t5-xxl"
            from langchain import HuggingFaceHub
            executor = HuggingFaceHub(repo_id=model_name)
        case "hiya":
            from hiya import Hiya
            executor = Hiya()
        case _:  # default to "openai"
            model_name = model_name or "text-davinci-003"
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

if __name__ == '__main__':
    app()