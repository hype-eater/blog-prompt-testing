import typer
from langchain import OpenAI, PromptTemplate

app = typer.Typer(help="A helpful and friendly CLI")

GREETING_PROMPT = "A greeting: "
INTRODUCTION_PROMPT_TMPL = PromptTemplate(
    input_variables=["name"],
    template="Hello, my name is {name}.",
)


@app.command()
def hello():
    """Say hello"""
    executor = get_prompt_executor()
    response = executor(GREETING_PROMPT)
    print(response.strip())


@app.command()
def intro(name: str = "User"):
    """Reply to an introduction"""
    executor = get_prompt_executor()
    prompt = INTRODUCTION_PROMPT_TMPL.format_prompt(name=name)
    response = executor(prompt.to_string())
    print(response.strip())


def get_prompt_executor(model_name="text-davinci-003"):
    executor = OpenAI(model_name=model_name)
    return executor


if __name__ == '__main__':
    app()