"""
Planner Agent

Decides the intent and the tool for a question.

Why this was rewritten
----------------------
The previous version matched keywords with plain `in` substring checks
against the whole lowercased query. Two of those lists were routing an
enormous share of ordinary questions down the slowest possible paths:

* `web_keywords` contained "new", "update", "version" and "release".
  "How do I create a new object in Java?" matched "new" and was sent to
  DuckDuckGo — a network round trip plus a 1000-token generation, for a
  question the model already knows cold.

* `rag_keywords` contained "java", "thread", "collection"... so nearly
  every question also paid a Chroma query plus an embedding call.

* `compiler_keywords` contained "run", so "How does the JVM run
  bytecode?" was handed to the Java compiler tool, which then failed to
  find code.

Matching is now word-boundary based, web search needs a recency signal
*and* a version/release signal, and RAG requires either an explicit
document reference or a domain term in a question long enough to be
worth retrieving for.
"""

import re
from typing import Iterable

from app.graph.state import AgentState
from app.config.logging_config import logger
from app.core.enums import ToolName, Intent


def _compile(words: Iterable[str]) -> re.Pattern:
    """Word-boundary alternation, longest first so phrases win."""
    ordered = sorted(set(words), key=len, reverse=True)
    escaped = [re.escape(w) for w in ordered]
    return re.compile(r"(?<!\w)(?:" + "|".join(escaped) + r")(?!\w)")


CODE_MARKERS = (
    "public class",
    "public static void main",
    "System.out.print",
    "```java",
    "```",
    "void main(",
    "@Override",
)

COMPILE_RE = _compile([
    "compile", "compiles", "recompile",
    "execute", "run this", "run it", "run the code", "run my code",
    "output of this", "what is the output", "what's the output",
])

REVIEW_RE = _compile([
    "review", "code review", "analyze", "analyse", "improve", "optimize",
    "optimise", "refactor", "clean up", "critique", "feedback",
])

RECENCY_RE = _compile([
    "latest", "newest", "recent", "recently", "currently", "current",
    "today", "this year", "2025", "2026", "news", "changelog",
])

VERSIONING_RE = _compile([
    "version", "release", "released", "lts", "roadmap", "jdk", "jep",
    "java 21", "java 22", "java 23", "java 24", "java 25",
    "spring boot 3", "spring boot 4", "deprecated",
])

DSA_RE = _compile([
    "leetcode", "hackerrank", "codeforces", "dsa",
    "coding problem", "coding challenge", "interview question",
    "brute force", "optimal solution", "dry run",
    "time complexity", "space complexity", "big o",
    "two pointer", "sliding window", "dynamic programming",
    "binary search", "linked list", "binary tree", "graph traversal",
])

DEBUG_RE = _compile([
    "nullpointerexception", "arrayindexoutofboundsexception",
    "classnotfoundexception", "nosuchmethodexception",
    "filenotfoundexception", "illegalargumentexception",
    "illegalstateexception", "stackoverflowerror", "outofmemoryerror",
    "arithmeticexception", "concurrentmodificationexception",
    "exception in thread", "stack trace", "stacktrace",
    "runtime error", "compile error", "compilation error",
    "why does this fail", "debug", "not working", "throws an error",
])

# Topics that are genuinely covered by the indexed PDFs/notes.
RAG_RE = _compile([
    "jvm", "jre", "classloader", "garbage collection", "gc",
    "spring", "spring boot", "hibernate", "jpa", "jdbc",
    "collections framework", "arraylist", "linkedlist", "hashmap",
    "concurrenthashmap", "multithreading", "executorservice",
    "rest api", "microservices", "design pattern", "solid",
    "checked exception", "unchecked exception", "generics", "streams api",
])

DOCUMENT_RE = _compile([
    "pdf", "document", "documents", "notes", "my notes", "the doc",
    "uploaded", "handbook", "syllabus", "according to the document",
])


def _has_code(raw_query: str) -> bool:
    return any(marker.lower() in raw_query.lower() for marker in CODE_MARKERS)


class PlannerAgent:
    # Below this word count a RAG lookup rarely improves the answer and
    # only adds an embedding call + a vector query to the latency.
    RAG_MIN_WORDS = 4

    def plan(self, state: AgentState) -> AgentState:
        raw = state["user_query"]
        query = raw.lower().strip()
        word_count = len(query.split())

        has_code = _has_code(raw)

        compiler_request = bool(COMPILE_RE.search(query)) and has_code
        review_request = bool(REVIEW_RE.search(query)) and has_code

        # Web search only when the user is clearly asking about something
        # time-sensitive, not merely using the word "new".
        web_request = bool(RECENCY_RE.search(query)) and bool(
            VERSIONING_RE.search(query)
        )

        dsa_request = bool(DSA_RE.search(query))
        debug_request = bool(DEBUG_RE.search(query))
        document_request = bool(DOCUMENT_RE.search(query))
        rag_request = document_request or (
            bool(RAG_RE.search(query)) and word_count >= self.RAG_MIN_WORDS
        )

        # Default
        intent = Intent.GENERAL.value
        tool = ToolName.LLM.value

        if compiler_request:
            tool = ToolName.JAVA_COMPILER.value

        elif review_request:
            tool = ToolName.REVIEW.value

        elif web_request:
            intent = Intent.WEB_SEARCH.value
            tool = ToolName.WEB.value

        elif dsa_request:
            intent = Intent.DSA.value
            tool = ToolName.DSA.value

        elif debug_request:
            # Debugging is answered by the LLM; retrieval on a stack trace
            # returns noise and costs a vector query.
            intent = Intent.DEBUG.value
            tool = ToolName.LLM.value

        elif rag_request:
            intent = Intent.RAG.value
            tool = ToolName.RAG.value

        state["intent"] = intent
        state["selected_tool"] = tool

        logger.info(f"Planner -> intent={intent} tool={tool}")
        return state
