# """
# Prompt Builder

# Builds the final prompt from the response plan.

# The previous template sent ~1,400 tokens of boilerplate rules with every
# single question. On a local model that is pure prefill latency paid on
# each turn. The rules below are condensed to the ones that actually change
# the output, which cuts roughly 70% of the fixed prompt size without
# losing the behaviour they were enforcing.
# """

# from typing import List, Optional

# SYSTEM_HEADER = (
#     "You are JavaMentorAI — a senior Java backend engineer, Spring Boot "
#     "expert and technical interview coach."
# )

# BASE_RULES = """Rules:
# - Treat any Retrieved Context as the primary source; fill gaps from your own Java knowledge and merge both into one answer.
# - Never say "according to the context/document".
# - Never repeat yourself or add sections beyond the required ones.
# - Finish every heading, list, sentence and code block you start. Prefer a complete short answer over a truncated long one.
# - When fixing a compile or runtime error, change only what that error requires. Define anything new you reference."""

# HISTORY_RULES = """Use the history ONLY to resolve references like "it", "that", "the above code".
# Treat the current question as an independent topic unless it explicitly refers back. Do not carry over unrelated concepts from earlier turns."""


# class PromptBuilder:
#     MAX_HISTORY_TURNS = 12
#     MAX_HISTORY_CHARS = 4000

#     def _format_turn(self, turn) -> str:
#         """
#         Handles both plain dicts and LangChain message objects, since
#         LangGraph's add_messages reducer may convert one into the other.
#         """
#         if isinstance(turn, dict):
#             role = turn.get("role", "user")
#             content = turn.get("content", "")
#         else:
#             msg_type = getattr(turn, "type", "human")
#             role = "user" if msg_type == "human" else "assistant"
#             content = getattr(turn, "content", "")

#         label = str(role).capitalize()
#         return f"{label}: {content}"

#     def _history_block(self, history: Optional[list]) -> str:
#         if not history:
#             return ""

#         turns: List[str] = []
#         used = 0

#         # Walk backwards so the most recent turns survive the budget.
#         for turn in reversed(history[-self.MAX_HISTORY_TURNS:]):
#             text = self._format_turn(turn)
#             if used + len(text) > self.MAX_HISTORY_CHARS:
#                 break
#             turns.append(text)
#             used += len(text)

#         if not turns:
#             return ""

#         joined = "\n".join(reversed(turns))
#         return f"\n## Conversation history\n{HISTORY_RULES}\n\n{joined}\n"

#     def build(
#         self,
#         question: str,
#         context: str,
#         response_plan: dict,
#         history: Optional[list] = None,
#     ) -> str:
#         style = response_plan.get("style")
#         if style == "conversational":
#             return self._build_conversational(question, history)
#         if style == "clarify":
#             return self._build_clarify(question, history)

#         sections = "\n".join(f"- {s}" for s in response_plan["sections"])

#         code_rule = (
#             "Include exactly ONE meaningful Java example that matches the question and uses realistic code, variable names, and output; avoid placeholders or fake stubs, such as a placeholder like 0, when a real example is possible."
#             if response_plan["include_code"]
#             else "Do NOT include a Java example."
#         )
#         detail_rule = (
#             "Include a detailed explanation."
#             if response_plan["include_details"]
#             else "Keep explanations brief."
#         )

#         context_block = (
#             f"\n## Retrieved context\n{context}\n" if context.strip() else ""
#         )

#         return f"""{SYSTEM_HEADER}
# {context_block}{self._history_block(history)}
# ## Question
# {question}

# ## Required answer format ({response_plan['style']})
# {sections}

# {code_rule}
# {detail_rule}

# {BASE_RULES}

# Return only the final answer."""

#     def _build_conversational(
#         self, question: str, history: Optional[list]
#     ) -> str:
#         """
#         For greetings and small talk. No sections, no forced Java topic —
#         the explainer template above was being applied even to "hi", which
#         left the model with nothing to explain and it would default to
#         rambling about a generic Java topic instead of just replying.
#         """
#         return f"""{SYSTEM_HEADER}
# {self._history_block(history)}
# The user just said: "{question}"

# This is small talk, not a technical question. Reply naturally in 1-2 short sentences, like a friendly mentor. Do not use headings, bullet points, or a Definition/Working/Conclusion structure. Do not explain an unrelated Java topic. You may invite them to ask a Java question.

# Return only your reply."""

#     def _build_clarify(self, question: str, history: Optional[list]) -> str:
#         """
#         For messages with no Java/programming content and no code — e.g.
#         "I have a question for you", "can you help me?". The old template
#         forced an explainer answer here too, so the model had to invent a
#         Java topic out of nothing. Ask what they need instead of guessing.
#         """
#         return f"""{SYSTEM_HEADER}
# {self._history_block(history)}
# The user said: "{question}"

# They have not asked a specific Java question yet — this message does not name one. Reply in 1-2 short sentences: acknowledge what they said, and ask them to share the specific Java question, error, or code they'd like help with. Do NOT guess a Java topic or give a technical explanation of anything. Do not use headings or bullet points.

# Return only your reply."""


"""
Prompt Builder

Builds the final prompt from the response plan.

The previous template sent ~1,400 tokens of boilerplate rules with every
single question. On a local model that is pure prefill latency paid on
each turn. The rules below are condensed to the ones that actually change
the output, which cuts roughly 70% of the fixed prompt size without
losing the behaviour they were enforcing.
"""

from typing import List, Optional

SYSTEM_HEADER = (
    "You are JavaMentorAI — a senior Java backend engineer, Spring Boot "
    "expert and technical interview coach."
)

BASE_RULES = """Rules:
- Treat any Retrieved Context as the primary source; fill gaps from your own Java knowledge and merge both into one answer.
- Never say "according to the context/document".
- Never repeat yourself or add sections beyond the required ones.
- Finish every heading, list, sentence and code block you start. Prefer a complete short answer over a truncated long one.
- When fixing a compile or runtime error, change only what that error requires. Define anything new you reference."""

HISTORY_RULES = """Use the history ONLY to resolve references like "it", "that", "the above code".
Treat the current question as an independent topic unless it explicitly refers back. Do not carry over unrelated concepts from earlier turns."""


class PromptBuilder:
    MAX_HISTORY_TURNS = 12
    MAX_HISTORY_CHARS = 4000

    def _format_turn(self, turn) -> str:
        """
        Handles both plain dicts and LangChain message objects, since
        LangGraph's add_messages reducer may convert one into the other.
        """
        if isinstance(turn, dict):
            role = turn.get("role", "user")
            content = turn.get("content", "")
        else:
            msg_type = getattr(turn, "type", "human")
            role = "user" if msg_type == "human" else "assistant"
            content = getattr(turn, "content", "")

        label = str(role).capitalize()
        return f"{label}: {content}"

    def _history_block(self, history: Optional[list]) -> str:
        if not history:
            return ""

        turns: List[str] = []
        used = 0

        # Walk backwards so the most recent turns survive the budget.
        for turn in reversed(history[-self.MAX_HISTORY_TURNS:]):
            text = self._format_turn(turn)
            if used + len(text) > self.MAX_HISTORY_CHARS:
                break
            turns.append(text)
            used += len(text)

        if not turns:
            return ""

        joined = "\n".join(reversed(turns))
        return f"\n## Conversation history\n{HISTORY_RULES}\n\n{joined}\n"

    def build(
        self,
        question: str,
        context: str,
        response_plan: dict,
        history: Optional[list] = None,
    ) -> str:
        style = response_plan.get("style")
        if style == "conversational":
            return self._build_conversational(question, history)
        if style == "clarify":
            return self._build_clarify(question, history)
        if style == "list":
            return self._build_list(question, context, history)

        sections = "\n".join(f"- {s}" for s in response_plan["sections"])

        code_rule = (
            "Include exactly ONE meaningful Java example that matches the question and uses realistic code, variable names, and output; avoid placeholders or fake stubs, such as a placeholder like 0, when a real example is possible."
            if response_plan["include_code"]
            else "Do NOT include a Java example."
        )
        detail_rule = (
            "Include a detailed explanation."
            if response_plan["include_details"]
            else "Keep explanations brief."
        )

        context_block = (
            f"\n## Retrieved context\n{context}\n" if context.strip() else ""
        )

        return f"""{SYSTEM_HEADER}
{context_block}{self._history_block(history)}
## Question
{question}

## Required answer format ({response_plan['style']})
{sections}

{code_rule}
{detail_rule}

{BASE_RULES}

Return only the final answer."""

    def _build_conversational(
        self, question: str, history: Optional[list]
    ) -> str:
        """
        For greetings and small talk. No sections, no forced Java topic —
        the explainer template above was being applied even to "hi", which
        left the model with nothing to explain and it would default to
        rambling about a generic Java topic instead of just replying.
        """
        return f"""{SYSTEM_HEADER}
{self._history_block(history)}
The user just said: "{question}"

This is small talk, not a technical question. Reply naturally in 1-2 short sentences, like a friendly mentor. Do not use headings, bullet points, or a Definition/Working/Conclusion structure. Do not explain an unrelated Java topic. You may invite them to ask a Java question.

Return only your reply."""

    def _build_list(
        self, question: str, context: str, history: Optional[list]
    ) -> str:
        """
        For requests like "give me 20 interview questions" or "list them
        one by one" — the person wants plain items, not an explained
        answer. Do NOT use the Definition/Working/Java Example/Conclusion
        template here at all.
        """
        context_block = (
            f"\n## Retrieved context\n{context}\n" if context.strip() else ""
        )
        return f"""{SYSTEM_HEADER}
{context_block}{self._history_block(history)}
## Question
{question}

The user wants a plain list of items (e.g. questions), not an explained answer. Rules:
- Do NOT use a Definition/Working/Example/Conclusion structure or any other fixed template.
- Do NOT add an introduction, summary, or conclusion paragraph.
- Output only the numbered list, one item per line, nothing else.
- Match the count the user asked for as closely as possible.

{BASE_RULES}

Return only the numbered list."""

    def _build_clarify(self, question: str, history: Optional[list]) -> str:
        """
        For messages with no Java/programming content and no code — e.g.
        "I have a question for you", "can you help me?". The old template
        forced an explainer answer here too, so the model had to invent a
        Java topic out of nothing. Ask what they need instead of guessing.
        """
        return f"""{SYSTEM_HEADER}
{self._history_block(history)}
The user said: "{question}"

They have not asked a specific Java question yet — this message does not name one. Reply in 1-2 short sentences: acknowledge what they said, and ask them to share the specific Java question, error, or code they'd like help with. Do NOT guess a Java topic or give a technical explanation of anything. Do not use headings or bullet points.

Return only your reply."""