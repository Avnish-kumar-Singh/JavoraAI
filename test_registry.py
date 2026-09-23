from app.tools.registry import ToolRegistry

registry = ToolRegistry()

print(registry.get_tool("llm"))
print(registry.get_tool("rag"))
print(registry.get_tool("web"))
print(registry.get_tool("dsa"))
print(registry.get_tool("review"))
print(registry.get_tool("java_compiler"))