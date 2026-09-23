"""
CLI entry point.

The HTTP API + web UI is the primary interface now:

    python run_api.py      →  http://localhost:8000
"""

import pyperclip
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

from app.core.container import get_graph

session = PromptSession()


def get_user_input() -> str:
    """
    Type a question and press Enter. To submit pasted multi-line code
    reliably, copy it to the clipboard, then type PASTE and press Enter.
    """
    text = session.prompt(HTML("<ansicyan><b>Ask JavaMentorAI:</b></ansicyan> "))

    if text.strip().upper() == "PASTE":
        return pyperclip.paste().strip()

    return text.strip()


def main():
    print("\nJavaMentorAI — type a question, or 'exit' to quit.")
    print("Type PASTE to submit Java code from your clipboard.\n")

    graph = get_graph()
    conversation_history = []

    while True:
        user_query = get_user_input()

        if not user_query:
            continue
        if user_query.lower() in ("exit", "quit"):
            break

        state = {
            "messages": conversation_history,
            "user_query": user_query,
            "intent": "",
            "selected_tool": "",
            "context": "",
            "response": "",
            "status": "",
            "error": "",
        }

        result = graph.invoke(state)
        response = result["response"]

        if isinstance(response, dict):
            response = response.get("message", str(response))
        elif not isinstance(response, str):
            response = str(response)

        print("\n" + "=" * 30)
        print(response)
        print("=" * 30 + "\n")

        conversation_history.append({"role": "user", "content": user_query})
        conversation_history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
