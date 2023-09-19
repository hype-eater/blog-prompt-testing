from promptimize import evals
from promptimize.prompt_cases import PromptCase, LangchainPromptCase

from app import GREETING_PROMPT, INTRODUCTION_PROMPT_TMPL, get_prompt_executor

import os

model = os.getenv("MODEL")
provider = os.getenv("PROVIDER")
prompt_executor = get_prompt_executor(model, provider)


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
    LangchainPromptCase(PYTHON_FUNCTION_PROMPT_TMPL,
                        key=f"code-hello-world",
                        category="code",
                        description="a function that returns the string 'Hello, World.'",
                        evaluators=[lambda x: evals.all_words(x.response, ["def"])],
                        prompt_executor=prompt_executor,
                        ),
    LangchainPromptCase(PYTHON_FUNCTION_PROMPT_TMPL,
                        key=f"code-is-prime",
                        category="code",
                        description="a function that tests if an number is a prime number, returns a boolean",
                        evaluators=[lambda x: evals.all_words(x.response, ["def"])],
                        prompt_executor=prompt_executor,
                        )
]