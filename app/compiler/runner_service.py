# """
# Runner Service
# """

# import subprocess
# from pathlib import Path


# class RunnerService:

#     def run(self, folder_path: Path) -> dict:
#         """
#         Execute the compiled Main.class file.
#         """

#         result = subprocess.run(
#             ["java", "Main"],
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
Runner Service
"""

import subprocess
from pathlib import Path


class RunnerService:

    def run(self, folder_path: Path, class_name: str = "Main") -> dict:
        """
        Execute the compiled <class_name>.class file.
        """

        result = subprocess.run(
            ["java", class_name],
            cwd=folder_path,
            capture_output=True,
            text=True
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }