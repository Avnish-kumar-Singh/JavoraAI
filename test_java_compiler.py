# """
# Test Java Compiler Tool
# """

# from app.tools.java_compiler_tool import JavaCompilerTool


# tool = JavaCompilerTool()


# code = """
# public class Main {
#     public static void main(String[] args) {
#         int x = 10 / 0;
#         System.out.println(x);
#     }
# }
# """


# result = tool.execute(code)

# print(result)







"""
Test Java Compiler Tool
"""

from app.tools.java_compiler_tool import JavaCompilerTool


def make_state(code: str) -> dict:
    return {
        "user_query": code,
        "messages": [],
        "intent": "",
        "selected_tool": "",
        "context": "",
        "response": "",
        "status": "",
        "error": "",
    }


def test_runtime_error_division_by_zero():
    tool = JavaCompilerTool()

    code = """
public class Main {
    public static void main(String[] args) {
        int x = 10 / 0;
        System.out.println(x);
    }
}
"""

    result = tool.execute(make_state(code))

    assert result["status"] == "RUNTIME_ERROR"
    assert "ArithmeticException" in result["response"]["exception"]

    print("✅ test_runtime_error_division_by_zero passed")


def test_compilation_error_missing_semicolon():
    tool = JavaCompilerTool()

    code = """
public class Broken {
    public static void main(String[] args) {
        int x = 5
        System.out.println(x);
    }
}
"""

    result = tool.execute(make_state(code))

    assert result["status"] == "COMPILATION_ERROR"
    assert "expected" in result["response"]["message"]

    print("✅ test_compilation_error_missing_semicolon passed")


def test_success_case():
    tool = JavaCompilerTool()

    code = """
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""

    result = tool.execute(make_state(code))

    assert result["status"] == "SUCCESS"
    assert "Hello" in result["response"]

    print("✅ test_success_case passed")


if __name__ == "__main__":
    test_runtime_error_division_by_zero()
    test_compilation_error_missing_semicolon()
    test_success_case()
    print("\nAll tests passed!")