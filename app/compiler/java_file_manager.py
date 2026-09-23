# """
# Java File Manager
# """

# import shutil
# import uuid
# from pathlib import Path


# class JavaFileManager:

#     def __init__(self):
#         self.temp_root = Path("app/temp")
#         self.temp_root.mkdir(parents=True, exist_ok=True)

#     def create_java_file(self, code: str):

#         # Create a unique folder
#         folder_path = self.temp_root / str(uuid.uuid4())
#         folder_path.mkdir(parents=True, exist_ok=True)

#         # Create Main.java
#         java_file = folder_path / "Main.java"

#         java_file.write_text(
#             code,
#             encoding="utf-8"
#         )

#         return folder_path, java_file

#     def cleanup(self, folder_path: Path):

#         if folder_path.exists():
#             shutil.rmtree(folder_path)











"""
Java File Manager
"""

import shutil
import uuid
from pathlib import Path


class JavaFileManager:

    def __init__(self):
        self.temp_root = Path("app/temp")
        self.temp_root.mkdir(parents=True, exist_ok=True)

    def create_java_file(self, code: str, class_name: str = "Main"):

        # Create a unique folder
        folder_path = self.temp_root / str(uuid.uuid4())
        folder_path.mkdir(parents=True, exist_ok=True)

        # File must match the public class name exactly
        java_file = folder_path / f"{class_name}.java"

        java_file.write_text(
            code,
            encoding="utf-8"
        )

        return folder_path, java_file

    def cleanup(self, folder_path: Path):

        if folder_path.exists():
            shutil.rmtree(folder_path)