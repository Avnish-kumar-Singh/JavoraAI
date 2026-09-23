from app.services.response_planner import ResponsePlanner
from app.synthesis.prompt_builder import PromptBuilder


def test_prompt_requires_realistic_java_example():
    question = "What is the difference between Java and Python?"
    plan = ResponsePlanner().plan(question)
    prompt = PromptBuilder().build(question, "", plan)

    text = prompt.lower()
    assert "meaningful java example" in text
    assert "placeholder like 0" in text or "not a placeholder" in text
