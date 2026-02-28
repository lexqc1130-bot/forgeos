import os
from abc import ABC, abstractmethod
from typing import Tuple


# ==============================
# Base Provider
# ==============================

class LLMProvider(ABC):

    @abstractmethod
    def generate_code(self, spec: str) -> Tuple[str, int]:
        pass

    @abstractmethod
    def repair_code(self, previous_code: str, error: str) -> Tuple[str, int]:
        pass


# ==============================
# Real Provider
# ==============================

class RealLLMProvider(LLMProvider):

    def generate_code(self, spec: str) -> Tuple[str, int]:
        from openai import OpenAI

        client = OpenAI()

        prompt = f"""
Generate a Python function named 'run'.
It must accept (org_id: str, **kwargs).
Task: {spec}
Return only pure Python code.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You generate safe python service functions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        code = response.choices[0].message.content

        tokens = 0
        if hasattr(response, "usage") and response.usage:
            usage = response.usage
            tokens = getattr(usage, "total_tokens", 0)

            if tokens == 0:
                tokens = (
                    getattr(usage, "prompt_tokens", 0)
                    + getattr(usage, "completion_tokens", 0)
                )

        return code, tokens


    def repair_code(self, previous_code: str, error: str) -> Tuple[str, int]:
        from openai import OpenAI

        client = OpenAI()

        prompt = f"""
The following Python function has an error.

Code:
{previous_code}

Error:
{error}

Fix the function.
Return only corrected pure Python code.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You fix python code safely."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        code = response.choices[0].message.content

        tokens = 0
        if hasattr(response, "usage") and response.usage:
            usage = response.usage
            tokens = getattr(usage, "total_tokens", 0)

            if tokens == 0:
                tokens = (
                    getattr(usage, "prompt_tokens", 0)
                    + getattr(usage, "completion_tokens", 0)
                )

        return code, tokens


# ==============================
# Mock Provider
# ==============================

class MockLLMProvider(LLMProvider):

    def generate_code(self, spec: str) -> Tuple[str, int]:

        code = """
def run(org_id: str, number: int, **kwargs):
    return number * number
"""
        return code, 0


    def repair_code(self, previous_code: str, error: str) -> Tuple[str, int]:

        # 假裝修好
        code = """
def run(org_id: str, number: int, **kwargs):
    return number * number
"""
        return code, 0


# ==============================
# Provider Selector
# ==============================

def get_llm_provider() -> LLMProvider:

    mode = os.getenv("FORGE_LLM_MODE", "mock")

    if mode == "real":
        return RealLLMProvider()

    return MockLLMProvider()