# """
# Java Compiler Tool
# """

# from app.tools.base_tool import BaseTool
# from app.compiler.java_file_manager import JavaFileManager
# from app.compiler.compiler_service import CompilerService
# from app.compiler.runner_service import RunnerService
# from app.compiler.error_parser import ErrorParser
# from app.config.logging_config import logger


# class JavaCompilerTool(BaseTool):

#     def __init__(self):

#         self.file_manager = JavaFileManager()
#         self.compiler = CompilerService()
#         self.runner = RunnerService()
#         self.error_parser = ErrorParser()

#     def execute(self, code: str):

#         logger.info("Java Compiler Tool Started")

#         folder_path, java_file = self.file_manager.create_java_file(code)

#         try:

#             # ----------------------------
#             # Compile
#             # ----------------------------

#             compile_result = self.compiler.compile(folder_path)

#             if not compile_result["success"]:

#                 return {
#                     "success": False,
#                     "response": self.error_parser.parse_compiler_error(
#                         compile_result["stderr"]
#                     )
#                 }

#             # ----------------------------
#             # Run
#             # ----------------------------

#             run_result = self.runner.run(folder_path)

#             if not run_result["success"]:

#                 return {
#                     "success": False,
#                     "response": self.error_parser.parse_runtime_error(
#                         run_result["stderr"]
#                     )
#                 }

#             # ----------------------------
#             # Success
#             # ----------------------------

#             return {
#                 "success": True,
#                 "response": run_result["stdout"]
#             }

#         finally:

#             self.file_manager.cleanup(folder_path)




# """
# Java Compiler Tool
# """
# 
# import re
# 
# from app.tools.base_tool import BaseTool
# from app.compiler.java_file_manager import JavaFileManager
# from app.compiler.compiler_service import CompilerService
# from app.compiler.runner_service import RunnerService
# from app.compiler.error_parser import ErrorParser
# from app.config.logging_config import logger
# 
# 
# class JavaCompilerTool(BaseTool):
# 
    # def __init__(self):
# 
        # self.file_manager = JavaFileManager()
        # self.compiler = CompilerService()
        # self.runner = RunnerService()
        # self.error_parser = ErrorParser()
# 
    # def execute(self, state):
# 
        # logger.info("Java Compiler Tool Started")
# 
        # Get the complete user query
        # query = state["user_query"]
# 
        # Extract Java code from the query
        # code = self.extract_java_code(query)
# 
        # if not code:
            # state["status"] = "FAILED"
            # state["response"] = "No Java code found."
            # return state
# 
        # folder_path, java_file = self.file_manager.create_java_file(code)
# 
        # try:
# 
            # ----------------------------
            # Compile
            # ----------------------------
            # compile_result = self.compiler.compile(folder_path)
# 
            # if not compile_result["success"]:
# 
                # state["status"] = "COMPILATION_ERROR"
                # state["response"] = self.error_parser.parse_compiler_error(
                    # compile_result["stderr"]
                # )
# 
                # return state
# 
            # ----------------------------
            # Run
            # ----------------------------
            # run_result = self.runner.run(folder_path)
# 
            # if not run_result["success"]:
# 
                # state["status"] = "RUNTIME_ERROR"
                # state["response"] = self.error_parser.parse_runtime_error(
                    # run_result["stderr"]
                # )
# 
                # return state
# 
            # ----------------------------
            # Success
            # ----------------------------
            # state["status"] = "SUCCESS"
            # state["response"] = run_result["stdout"]
# 
            # return state
# 
        # finally:
# 
            # self.file_manager.cleanup(folder_path)
# 
    # def extract_java_code(self, query: str):
        # """
        # Extract only the Java source code from the user's query.
# 
        # Supports:
        # - Plain Java code
        # - Markdown code blocks
        # - Additional text before the code
        # - Additional text after the code
        # """
# 
        # ----------------------------
        # Case 1: Markdown code block
        # ----------------------------
        # pattern = r"```(?:java)?\s*(.*?)```"
# 
        # match = re.search(
            # pattern,
            # query,
            # re.DOTALL | re.IGNORECASE
        # )
# 
        # if match:
            # return match.group(1).strip()
# 
        # ----------------------------
        # Case 2: Locate Java class
        # ----------------------------
        # class_pattern = r"(public\s+class|class)\s+\w+"
# 
        # match = re.search(class_pattern, query)
# 
        # if not match:
            # return None
# 
        # start = match.start()
        # code = query[start:]
# 
        # brace_count = 0
        # started = False
# 
        # for index, char in enumerate(code):
# 
            # if char == "{":
                # brace_count += 1
                # started = True
# 
            # elif char == "}":
                # brace_count -= 1
# 
                # if started and brace_count == 0:
                    # return code[: index + 1].strip()
# 
        # If braces are unbalanced, return the extracted code
        # return code.strip()
        
        
        
        
        
        
"""
Java Compiler Tool
"""

import re

from app.tools.base_tool import BaseTool
from app.compiler.java_file_manager import JavaFileManager
from app.compiler.compiler_service import CompilerService
from app.compiler.runner_service import RunnerService
from app.compiler.error_parser import ErrorParser
from app.config.logging_config import logger


class JavaCompilerTool(BaseTool):

    def __init__(self):

        self.file_manager = JavaFileManager()
        self.compiler = CompilerService()
        self.runner = RunnerService()
        self.error_parser = ErrorParser()

    def execute(self, state):

        logger.info("Java Compiler Tool Started")

        # Get the complete user query
        query = state["user_query"]

        # Extract Java code from the query
        code = self.extract_java_code(query)

        if not code:
            state["status"] = "FAILED"
            state["response"] = "No Java code found."
            return state

        # Extract class name so file name and run command match it
        class_name = self.get_class_name(code)

        folder_path, java_file = self.file_manager.create_java_file(
            code,
            class_name
        )

        try:

            # ----------------------------
            # Compile
            # ----------------------------
            compile_result = self.compiler.compile(folder_path, class_name)

            if not compile_result["success"]:

                state["status"] = "COMPILATION_ERROR"
                state["response"] = self.error_parser.parse_compiler_error(
                    compile_result["stderr"]
                )

                return state

            # ----------------------------
            # Run
            # ----------------------------
            run_result = self.runner.run(folder_path, class_name)

            if not run_result["success"]:

                state["status"] = "RUNTIME_ERROR"
                state["response"] = self.error_parser.parse_runtime_error(
                    run_result["stderr"]
                )

                return state

            # ----------------------------
            # Success
            # ----------------------------
            state["status"] = "SUCCESS"
            state["response"] = run_result["stdout"]

            return state

        finally:

            self.file_manager.cleanup(folder_path)

    def extract_java_code(self, query: str):
        """
        Extract only the Java source code from the user's query.

        Supports:
        - Plain Java code
        - Markdown code blocks
        - Additional text before the code
        - Additional text after the code
        """

        # ----------------------------
        # Case 1: Markdown code block
        # ----------------------------
        pattern = r"```(?:java)?\s*(.*?)```"

        match = re.search(
            pattern,
            query,
            re.DOTALL | re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

        # ----------------------------
        # Case 2: Locate Java class
        # ----------------------------
        class_pattern = r"(public\s+class|class)\s+\w+"

        match = re.search(class_pattern, query)

        if not match:
            return None

        start = match.start()
        code = query[start:]

        brace_count = 0
        started = False

        for index, char in enumerate(code):

            if char == "{":
                brace_count += 1
                started = True

            elif char == "}":
                brace_count -= 1

                if started and brace_count == 0:
                    return code[: index + 1].strip()

        # If braces are unbalanced, return the extracted code
        return code.strip()

    def get_class_name(self, code: str) -> str:
        """
        Extract the public class name so the .java file
        and 'java <ClassName>' run command match it.
        Falls back to 'Main' if no class is found.
        """

        match = re.search(r"public\s+class\s+(\w+)", code)

        if match:
            return match.group(1)

        match = re.search(r"\bclass\s+(\w+)", code)

        if match:
            return match.group(1)

        return "Main"