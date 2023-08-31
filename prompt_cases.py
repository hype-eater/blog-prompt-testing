from promptimize import evals
from promptimize.prompt_cases import PromptCase, LangchainPromptCase

from app import GREETING_PROMPT, INTRODUCTION_PROMPT_TMPL, get_prompt_executor

prompt_executor = get_prompt_executor()

simple_prompt_cases = [
    PromptCase(GREETING_PROMPT,
               key="greeting",
               category="greeting",
               evaluators=[lambda x: evals.any_word(x.response, ["hello", "hi", "hey", "hiya"])],
               prompt_executor=prompt_executor,
               ),
    ]

intro_tmpl_cases = [
    LangchainPromptCase(INTRODUCTION_PROMPT_TMPL,
                        key="intro-kitty",
                        category="intro",
                        name="Kitty",
                        evaluators=[lambda x: evals.all_words(x.response, ["Kitty", ]),
                                    lambda x: evals.any_word(x.response, ["nice", "hi", "hello"])],
                        prompt_executor=prompt_executor,
                        ),
]