import re
from typing import Optional, List, Any
from langchain.llms.base import LLM


class Hiya(LLM):
    @property
    def _llm_type(self) -> str:
        return "hiya"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager=None, **kwargs: Any) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        m = re.search(r'me *([^.]*)\.', prompt, flags=re.IGNORECASE)
        return f"Hiya {m.group(1) if m else 'there'}!"