# """
# Response Planner

# Decides response length, sections, and whether to include code.

# Three tiers before any explainer template is even considered:
# 1. Pure small talk ("hi", "thanks")            -> short natural reply.
# 2. No Java/programming content at all          -> ask what they need,
#    ("I have a question for you", "can you help me?")   don't guess a topic.
# 3. An actual technical question                -> the explainer template.

# Skipping tiers 1-2 was the original bug: everything short with no code
# or "explain"-style keyword fell straight into a Definition/Working/
# Conclusion template, so a message with nothing technical in it still
# forced the model to invent SOME Java topic to fill the structure.
# """

# import re

# from app.config.settings import settings
# from app.core.text import has_technical_content, is_smalltalk

# DEPTH_RE = re.compile(
#     r"(?<!\w)(explain|internally|internal|architecture|under the hood|"
#     r"deep dive|in detail|detailed|walk me through|compare|difference between|"
#     r"why does|how does|step by step)(?!\w)",
#     re.IGNORECASE,
# )

# CODE_RE = re.compile(
#     r"(?<!\w)(example|examples|sample|snippet|code|implement|implementation|"
#     r"write|show me|demo|program)(?!\w)",
#     re.IGNORECASE,
# )


# class ResponsePlanner:
#     SHORT_WORD_LIMIT = 5

#     def plan(self, question: str) -> dict:
#         if is_smalltalk(question):
#             return {
#                 "max_tokens": min(150, settings.SHORT_RESPONSE_TOKENS),
#                 "style": "conversational",
#                 "sections": [],
#                 "include_code": False,
#                 "include_details": False,
#             }

#         if not has_technical_content(question):
#             return {
#                 "max_tokens": min(150, settings.SHORT_RESPONSE_TOKENS),
#                 "style": "clarify",
#                 "sections": [],
#                 "include_code": False,
#                 "include_details": False,
#             }

#         words = question.split()
#         wants_code = bool(CODE_RE.search(question))
#         wants_depth = bool(DEPTH_RE.search(question))

#         # A terse question gets a terse answer — unless it explicitly asks
#         # for code ("HashMap example" is 2 words and needs a snippet).
#         if len(words) <= self.SHORT_WORD_LIMIT and not wants_code and not wants_depth:
#             return {
#                 "max_tokens": settings.SHORT_RESPONSE_TOKENS,
#                 "style": "short",
#                 "sections": ["Definition", "Working", "Conclusion"],
#                 "include_code": False,
#                 "include_details": False,
#             }

#         if wants_depth:
#             return {
#                 "max_tokens": settings.LONG_RESPONSE_TOKENS,
#                 "style": "long",
#                 "sections": [
#                     "Definition",
#                     "Working",
#                     "Java Example",
#                     "Detailed Explanation",
#                     "Conclusion",
#                 ],
#                 "include_code": True,
#                 "include_details": True,
#             }

#         return {
#             "max_tokens": settings.MEDIUM_RESPONSE_TOKENS,
#             "style": "medium",
#             "sections": ["Definition", "Working", "Java Example", "Conclusion"],
#             "include_code": True,
#             "include_details": False,
#         }


"""
Response Planner

Decides response length, sections, and whether to include code.

Three tiers before any explainer template is even considered:
1. Pure small talk ("hi", "thanks")            -> short natural reply.
2. No Java/programming content at all          -> ask what they need,
   ("I have a question for you", "can you help me?")   don't guess a topic.
3. An actual technical question                -> the explainer template.

Skipping tiers 1-2 was the original bug: everything short with no code
or "explain"-style keyword fell straight into a Definition/Working/
Conclusion template, so a message with nothing technical in it still
forced the model to invent SOME Java topic to fill the structure.
"""

import re

from app.config.settings import settings
from app.core.text import has_technical_content, is_smalltalk

DEPTH_RE = re.compile(
    r"(?<!\w)(explain|internally|internal|architecture|under the hood|"
    r"deep dive|in detail|detailed|walk me through|compare|difference between|"
    r"why does|how does|step by step)(?!\w)",
    re.IGNORECASE,
)

CODE_RE = re.compile(
    r"(?<!\w)(example|examples|sample|snippet|code|implement|implementation|"
    r"write|show me|demo|program)(?!\w)",
    re.IGNORECASE,
)

# A request for a plain list of questions/items rather than an explained
# answer — "give me 20 questions", "list interview questions", "one by
# one", "no template", "without definition/working/example". When this
# matches, skip the Definition/Working/Example/Conclusion template
# entirely and just return the list.
LIST_RE = re.compile(
    r"(?<!\w)(\d+\s*(-\s*\d+\s*)?questions?|list\s+(of\s+)?questions?|"
    r"one by one|no template|without\s+(a\s+)?template|"
    r"just\s+(the\s+)?questions?|only\s+questions?)(?!\w)",
    re.IGNORECASE,
)


class ResponsePlanner:
    SHORT_WORD_LIMIT = 5

    def plan(self, question: str) -> dict:
        if is_smalltalk(question):
            return {
                "max_tokens": min(150, settings.SHORT_RESPONSE_TOKENS),
                "style": "conversational",
                "sections": [],
                "include_code": False,
                "include_details": False,
            }

        if not has_technical_content(question):
            return {
                "max_tokens": min(150, settings.SHORT_RESPONSE_TOKENS),
                "style": "clarify",
                "sections": [],
                "include_code": False,
                "include_details": False,
            }

        if LIST_RE.search(question):
            return {
                "max_tokens": settings.LONG_RESPONSE_TOKENS,
                "style": "list",
                "sections": [],
                "include_code": False,
                "include_details": False,
            }

        words = question.split()
        wants_code = bool(CODE_RE.search(question))
        wants_depth = bool(DEPTH_RE.search(question))

        # A terse question gets a terse answer — unless it explicitly asks
        # for code ("HashMap example" is 2 words and needs a snippet).
        if len(words) <= self.SHORT_WORD_LIMIT and not wants_code and not wants_depth:
            return {
                "max_tokens": settings.SHORT_RESPONSE_TOKENS,
                "style": "short",
                "sections": ["Definition", "Working", "Conclusion"],
                "include_code": False,
                "include_details": False,
            }

        if wants_depth:
            return {
                "max_tokens": settings.LONG_RESPONSE_TOKENS,
                "style": "long",
                "sections": [
                    "Definition",
                    "Working",
                    "Java Example",
                    "Detailed Explanation",
                    "Conclusion",
                ],
                "include_code": True,
                "include_details": True,
            }

        return {
            "max_tokens": settings.MEDIUM_RESPONSE_TOKENS,
            "style": "medium",
            "sections": ["Definition", "Working", "Java Example", "Conclusion"],
            "include_code": True,
            "include_details": False,
        }