"""
Shared text classification used by the response planner (to pick a
prompt style) and the chat service (to title sessions sensibly).
"""

import re

_PUNCT_RE = re.compile(r"[!?.,;:]+")
_WHITESPACE_RE = re.compile(r"\s+")

# Whole-message matches only — a greeting embedded in a real question
# ("hi, what's a HashMap?") should NOT count as small talk.
SMALLTALK_PHRASES = {
    "hi", "hii", "hiii", "hiiii", "hello", "hello there", "hey", "heyy",
    "yo", "sup", "hola", "hi there", "hey there",
    "hi chat", "hii chat", "hello chat", "hey chat",
    "good morning", "good afternoon", "good evening",
    "how are you", "hows it going", "whats up",
    "thanks", "thank you", "thx", "ty", "thanks a lot",
    "bye", "goodbye", "see you", "cya",
    "ok", "okay", "cool", "nice", "great", "got it",
    "test", "testing",
}

# Terms that indicate the message is actually about Java/programming.
# Kept broad on purpose: false negatives (missing a real question) are
# worse here than false positives.
_TECH_TERMS = [
    "java", "jvm", "jdk", "jre", "class", "object", "interface", "package",
    "import", "annotation", "generic", "generics", "lambda", "stream",
    "optional", "collection", "collections", "arraylist", "linkedlist",
    "hashmap", "hashset", "treemap", "map", "list", "set", "queue", "deque",
    "array", "string", "variable", "constructor", "inheritance",
    "polymorphism", "encapsulation", "abstraction", "abstract", "static",
    "final", "overload", "overriding", "override", "exception", "throw",
    "throws", "try catch", "null", "nullpointer", "pointer", "stack",
    "heap", "compile", "compiler", "compilation", "syntax", "debug",
    "error", "bug", "crash", "fix", "runtime", "output", "return",
    "loop", "recursion", "recursive", "sort", "sorting", "search",
    "algorithm", "complexity", "big o", "data structure", "thread",
    "threading", "concurrency", "synchronized", "volatile", "singleton",
    "design pattern", "solid", "oop", "object oriented", "iterator",
    "comparator", "comparable", "spring", "springboot", "hibernate",
    "jdbc", "rest api", "microservice", "maven", "gradle", "leetcode",
    "hackerrank", "interview", "interview question", "interview questions",
    "mock interview", "coding question", "coding questions",
    "practice question", "practice questions", "code", "program", "programming",
    "method", "function", ".java",
    "jit", "gc", "bytecode", "classloader", "garbage collection", "api",
    "sdk", "ide", "enum", "autoboxing", "unboxing", "varargs", "wrapper class",
    "immutable", "mutable", "multithreading",
]
TECH_RE = re.compile(
    r"(?<!\w)(" + "|".join(re.escape(t) for t in _TECH_TERMS) + r")(?!\w)",
    re.IGNORECASE,
)

CODE_BLOCK_RE = re.compile(
    r"```|public\s+class|public\s+static\s+void\s+main|System\.out",
    re.IGNORECASE,
)


def normalize(text: str) -> str:
    stripped = _PUNCT_RE.sub("", text).strip().lower()
    return _WHITESPACE_RE.sub(" ", stripped)


def is_smalltalk(text: str) -> bool:
    """True only when the WHOLE message is a greeting/pleasantry."""
    return normalize(text) in SMALLTALK_PHRASES


def has_technical_content(text: str) -> bool:
    """True if the message references Java/programming at all, or
    contains an actual code block."""
    return bool(TECH_RE.search(text)) or bool(CODE_BLOCK_RE.search(text))