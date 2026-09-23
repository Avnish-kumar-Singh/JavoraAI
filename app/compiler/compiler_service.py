# """
# Compiler Service
# """

# import subprocess
# from pathlib import Path


# class CompilerService:

#     def compile(self, folder_path: Path) -> dict:
#         """
#         Compile Main.java inside the given folder.
#         """

#         result = subprocess.run(
#             ["javac", "Main.java"],
#             cwd=folder_path,
#             capture_output=True,
#             text=True
#         )

#         return {
#             "success": result.returncode == 0,
#             "stdout": result.stdout,
#             "stderr": result.stderr
#         }





"""
Compiler Service
"""

import subprocess
from pathlib import Path


class CompilerService:

    def compile(self, folder_path: Path, class_name: str = "Main") -> dict:
        """
        Compile <class_name>.java inside the given folder.
        """

        result = subprocess.run(
            ["javac", f"{class_name}.java"],
            cwd=folder_path,
            capture_output=True,
            text=True
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }