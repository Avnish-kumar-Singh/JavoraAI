"""
Error Parser
"""

import re


class ErrorParser:

    def parse_compiler_error(self, stderr: str) -> dict:
        """
        Parse Java compilation errors.
        """

        line_number = None

        match = re.search(r"Main\.java:(\d+):", stderr)

        if match:
            line_number = int(match.group(1))

        return {
            "type": "Compilation Error",
            "line": line_number,
            "message": stderr.strip()
        }

    def parse_runtime_error(self, stderr: str) -> dict:
        """
        Parse Java runtime errors.
        """

        exception = None

        match = re.search(r"Exception in thread.*?([\w\.]+):", stderr)

        if match:
            exception = match.group(1)

        return {
            "type": "Runtime Error",
            "exception": exception,
            "message": stderr.strip()
        }