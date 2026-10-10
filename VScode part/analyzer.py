"""Python AST inspection tool; it never imports or executes the target file."""
import ast
from pathlib import Path
from typing import Any, Dict


def analyze_python(path: str, workspace: str = "workspace") -> Dict[str, Any]:
    target = (Path(workspace) / path).resolve()
    root = Path(workspace).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return {"success": False, "error": "Access denied."}
    if target.suffix != ".py" or not target.is_file():
        return {"success": False, "error": "Python file does not exist."}
    source = target.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(target))
    except SyntaxError as error:
        return {"success": True, "valid": False, "error": str(error)}
    nodes = list(ast.walk(tree))
    loops = [node for node in nodes if isinstance(node, (ast.For, ast.AsyncFor, ast.While))]
    loop_depths = []

    def visit_depth(node, depth=0):
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            depth += 1
            loop_depths.append(depth)
        for child in ast.iter_child_nodes(node):
            visit_depth(child, depth)

    visit_depth(tree)
    complexity = 1 + sum(
        isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp))
        for node in nodes
    )
    optimizations = []
    if max(loop_depths, default=0) > 1:
        optimizations.append({
            "type": "nested_loop",
            "severity": "medium",
            "message": "Nested loop detected.",
            "suggestion": "Consider indexing, caching, or vectorization where behavior permits.",
        })
    if any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
           and node.func.attr == "append" for node in nodes):
        optimizations.append({
            "type": "list_append",
            "severity": "low",
            "message": "List append operations detected.",
            "suggestion": "Consider a comprehension only when it remains clear and measurable.",
        })
    return {
        "success": True,
        "valid": True,
        "imports": [
            alias.name if isinstance(node, ast.Import) else (node.module or "")
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in (node.names if isinstance(node, ast.Import) else [node.names[0]])
        ],
        "functions": [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))],
        "classes": [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)],
        "lines": len(source.splitlines()),
        "statistics": {
            "lines": len(source.splitlines()),
            "functions": sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in nodes),
            "classes": sum(isinstance(node, ast.ClassDef) for node in nodes),
            "loops": len(loops),
            "nested_loops": sum(depth > 1 for depth in loop_depths),
            "ifs": sum(isinstance(node, ast.If) for node in nodes),
            "imports": sum(isinstance(node, (ast.Import, ast.ImportFrom)) for node in nodes),
        },
        "complexity": {
            "cyclomatic": complexity,
            "max_nesting_depth": max(loop_depths, default=0),
        },
        "numpy": {"used": any(
            (isinstance(node, ast.Import) and any(alias.name == "numpy" for alias in node.names))
            or (isinstance(node, ast.ImportFrom) and node.module == "numpy")
            for node in nodes
        )},
        "optimizations": optimizations,
    }


def analyze_python_source(source: str) -> Dict[str, Any]:
    """Analyze submitted source without writing or executing it."""
    tree = ast.parse(source, filename="<submitted>")
    nodes = list(ast.walk(tree))
    return {
        "success": True,
        "valid": True,
        "statistics": {
            "lines": len(source.splitlines()),
            "functions": sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in nodes),
            "classes": sum(isinstance(node, ast.ClassDef) for node in nodes),
            "loops": sum(isinstance(node, (ast.For, ast.AsyncFor, ast.While)) for node in nodes),
            "ifs": sum(isinstance(node, ast.If) for node in nodes),
            "imports": sum(isinstance(node, (ast.Import, ast.ImportFrom)) for node in nodes),
        },
    }
