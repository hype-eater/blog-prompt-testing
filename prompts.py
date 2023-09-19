from langchain import PromptTemplate

PYTHON_FUNCTION_TMPL = """\
System: you are an AI that writes Python functions

Python guidelines:
* follow the PEP8 conventions
* provide type hints

User: write a function that multiplies a number by 2 and returns the result

System:
def multiply_by_2(number: int | float | complex) -> int | float | complex:
    return number * 2

User: {description}

System:
"""

PYTHON_FUNCTION_PROMPT_TMPL = PromptTemplate(
    input_variables=["description"],
    template=PYTHON_FUNCTION_TMPL,
)