import typer
from langchain import OpenAI, PromptTemplate

from enum import Enum


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


if __name__ == '__main__':
    app()