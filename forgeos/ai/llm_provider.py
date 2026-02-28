import os


class LLMProvider:
    def generate_code(self, spec: str) -> str:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    def generate_code(self, spec: str) -> str:
        if "square" in spec:
            return """def run(org_id: str, number: int, **kwargs):
    return number * number
"""
        return """def run(org_id: str, **kwargs):
    return "mock_default"
"""


class RealLLMProvider(LLMProvider):
    def generate_code(self, spec: str) -> str:
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

        return response.choices[0].message.content


def get_llm_provider() -> LLMProvider:
    mode = os.getenv("FORGE_LLM_MODE", "mock")

    if mode == "real":
        return RealLLMProvider()

    return MockLLMProvider()