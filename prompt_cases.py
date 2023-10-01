from promptimize import evals
from promptimize.prompt_cases import PromptCase, LangchainPromptCase, BasePromptCase
from black import InvalidInput
from app import GREETING_PROMPT, INTRODUCTION_PROMPT_TMPL, get_prompt_executor, format_code, \
    exec_code_and_return_function, create_service_context
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


class QueryEngineQueryExecutor:
    def __init__(self, query_engine):
        self.query_engine = query_engine

    def __call__(self, text):
        ret = self.query_engine.query(text)
        return ret.response


class LlamaIndexQueryCase(BasePromptCase):

    attributes_used_for_hash = BasePromptCase.attributes_used_for_hash | {"query_str"}

    def __init__(
            self,
            query_str,
            service_context=None,
            query_engine=None,
            *args,
            **kwargs,
    ) -> None:
        self.query_str = query_str
        self.service_context = service_context or self._get_service_context()
        self.query_engine = query_engine or self._get_query_engine(service_context=service_context, *args, **kwargs,)
        super().__init__(prompt_executor=QueryEngineQueryExecutor(self.query_engine), *args, **kwargs)

    @staticmethod
    def _get_service_context():
        model = os.environ.get('MODEL')
        provider = os.getenv("PROVIDER")
        embed_model = os.getenv("EMBED_MODEL")
        embed_provider = os.getenv("EMBED_PROVIDER")
        service_context = create_service_context(model_name=model,
                                                 provider=provider,
                                                 embed_model=embed_model,
                                                 embed_provider=embed_provider)
        return service_context

    @staticmethod
    def _get_query_engine(service_context, *args, **kwargs):
        raise NotImplementedError()

    def render(self):
        return self.query_str


from query_engines import get_empty_index_query_engine

class LlamaEmptyIndexQueryCase(LlamaIndexQueryCase):
    @staticmethod
    def _get_query_engine(service_context, *args, **kwargs):
        return get_empty_index_query_engine(service_context)


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

empty_index_case = LlamaEmptyIndexQueryCase(key=f"empty-hello",
                                            category="llama-index",
                                            query_str="Hello?",
                                            evaluators=[lambda x: evals.any_word(x.response,
                                                                                 ["hello", "hi", "howdy", "welcome",
                                                                                  "good day", "good morning",
                                                                                  "good evening",
                                                                                  "hey", "hiya", "what's up"])],
                                            )

from query_engines import get_df_query_engine

class LlamaPandasDataframeQueryCase(LlamaIndexQueryCase):

    attributes_used_for_hash = LlamaIndexQueryCase.attributes_used_for_hash | {"df"}

    def __init__(
            self,
            df,
            *args,
            **kwargs,
    ) -> None:
        self.df = df
        super().__init__(df=self.df, *args, **kwargs)

    @staticmethod
    def _get_query_engine(service_context, *args, **kwargs):
        df = kwargs.get('df')
        return get_df_query_engine(service_context, df=df)

from query_engines import create_city_stats_df

llama_pandas_cases = [
    LlamaPandasDataframeQueryCase(df=create_city_stats_df(),
                                  key=f"pandas-largest-city",
                                  category="llama-index",
                                  query_str="What city has the largest population?",
                                  evaluators=[lambda x: evals.all_words(x.response,
                                                                        ["Tokyo", ]),
                                              lambda x: 1 - evals.any_word(x.response,
                                                                           ["Toronto",
                                                                            "Chicago",
                                                                            "Seoul", ]),
                                              ]
                                  ),
    LlamaPandasDataframeQueryCase(df=create_city_stats_df(),
                                  key=f"pandas-average-pop",
                                  category="llama-index",
                                  query_str="What is the average population?",
                                  evaluators=[lambda x: float(x.response.strip()) == 7336250.0]
                                  ),

]

from query_engines import get_db_query_engine

class LlamaSQLDatabaseQueryCase(LlamaIndexQueryCase):

    attributes_used_for_hash = LlamaIndexQueryCase.attributes_used_for_hash | {"table_info"}

    def __init__(
            self,
            sql_database,
            *args,
            **kwargs,
    ) -> None:
        self.sql_database = sql_database
        self.table_info = self.sql_database.table_info
        super().__init__(sql_database=self.sql_database,
                         *args, **kwargs)

    @staticmethod
    def _get_query_engine(service_context, *args, **kwargs):
        sql_database = kwargs.get('sql_database')
        query_engine = get_db_query_engine(service_context, sql_database=sql_database)
        return query_engine

from query_engines import create_and_populate_city_stats_db

llama_sql_cases = [
    LlamaSQLDatabaseQueryCase(sql_database=create_and_populate_city_stats_db(),
                              key=f"sql-largest-city",
                              category="llama-index",
                              query_str="What city has the largest population?",
                              evaluators=[lambda x: evals.all_words(x.response,
                                                                    ["Tokyo", ]),
                                          lambda x: 1 - evals.any_word(x.response,
                                                                       ["Toronto", "Chicago", "Seoul", ]),
                                          ]
                              ),
    LlamaSQLDatabaseQueryCase(sql_database=create_and_populate_city_stats_db(),
                              key=f"sql-average-pop",
                              category="llama-index",
                              query_str="What is the average population?",
                              evaluators=[lambda x: evals.any_word(x.response,
                                                                    ["7336250",
                                                                     "7,336,250",
                                                                     "7336250.0"])]
                              ),
]