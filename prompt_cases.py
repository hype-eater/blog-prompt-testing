from promptimize import evals
from promptimize.prompt_cases import PromptCase, LangchainPromptCase
from black import InvalidInput
from app import GREETING_PROMPT, INTRODUCTION_PROMPT_TMPL, get_prompt_executor, format_code, \
    exec_code_and_return_function
import os

model = os.getenv("MODEL")
provider = os.getenv("PROVIDER")
prompt_executor = get_prompt_executor(model, provider)


class PythonFunctionPromptCase(LangchainPromptCase):
    gen_fun = None

    def post_run(self):
        try:
            formatted_code = format_code(self.response)
            self.gen_fun = exec_code_and_return_function(formatted_code)
        except Exception as e:
            self.error = str(e)


def greeting_case(prompt_executor, index: str | int) -> PromptCase:
    greeting_words = ["hello", "hi", "howdy", "welcome", "good day", "good morning",
                      "good evening", "hey", "hiya", "what's up"]
    return PromptCase(GREETING_PROMPT,
                      key=f"greeting-{index}",
                      category="greeting",
                      evaluators=[lambda x: evals.any_word(x.response, greeting_words)],
                      prompt_executor=prompt_executor,
                      )


simple_prompt_cases = [greeting_case(prompt_executor, index) for index in range(5)]


def intro_case_for_name(prompt_executor, name: str) -> LangchainPromptCase:
    return LangchainPromptCase(INTRODUCTION_PROMPT_TMPL,
                               key=f"intro-{name.lower()}",
                               category="intro",
                               name=name,
                               evaluators=[lambda x: evals.all_words(x.response, [name, ]),
                                           lambda x: evals.any_word(x.response, ["nice", "hi", "hello"])],
                               prompt_executor=prompt_executor,
                               )


names = ["Kitty", "bob", "you", "ME", "who"]
intro_tmpl_cases = [intro_case_for_name(prompt_executor, name) for name in names]

from prompts import PYTHON_FUNCTION_PROMPT_TMPL

code_cases = [
    PythonFunctionPromptCase(PYTHON_FUNCTION_PROMPT_TMPL,
                             key=f"code-hello-world",
                             category="code",
                             description="a function that returns the string 'Hello, World.'",
                             evaluators=[lambda x: function_call_eval(x.gen_fun,
                                                                      expected_output='Hello, World.')],
                             prompt_executor=prompt_executor,
                             ),
    PythonFunctionPromptCase(PYTHON_FUNCTION_PROMPT_TMPL,
                             key=f"code-is-prime",
                             category="code",
                             description="a function that tests if an number is a prime number, returns a boolean",
                             evaluators=[lambda x: function_call_eval(x.gen_fun,
                                                                      args=[3],
                                                                      expected_output=True),
                                         lambda x: function_call_eval(x.gen_fun,
                                                                      args=[10],
                                                                      expected_output=False),
                                         lambda x: function_call_eval(x.gen_fun,
                                                                      args=[113],
                                                                      expected_output=True),
                                         ],
                             prompt_executor=prompt_executor,
                             ),
    PythonFunctionPromptCase(PYTHON_FUNCTION_PROMPT_TMPL,
                             key=f"code-add",
                             category="code",
                             description="a function that sum two numbers, 'x' and 'y'",
                             evaluators=[lambda x: function_call_eval(x.gen_fun,
                                                                      kwargs={"x": 1.5, "y": 10.5},
                                                                      expected_output=12.0),
                                         lambda x: function_call_eval(x.gen_fun,
                                                                      args=[45, -90],
                                                                      expected_output=-45),
                                         ],
                             prompt_executor=prompt_executor,
                             )
]

def valid_python_eval(response: str) -> int:
    try:
        format_code(response)
        return 1
    except InvalidInput:
        return 0

def function_call_eval(fun, args=None, kwargs=None, expected_output=None):
    args = args or []
    kwargs = kwargs or {}
    try:
        res = fun(*args, **kwargs)
        assert res == expected_output
        return 1
    except Exception:
        return 0
