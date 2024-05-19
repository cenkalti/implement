import ast
import inspect


def extract(func: callable) -> str:
    """Extract the source code of a function and its annotations."""
    module = inspect.getmodule(func)
    classes = {getattr(module, name, None) for name in _annotation_names(func)}
    classes.discard(None)

    result = []
    for cls in sorted(classes, key=lambda cls: cls.__name__):
        if inspect.isclass(cls) and cls.__module__ != 'builtins':
            result.append(_comment_out(_remove_function_body(cls)))

    result.append(_remove_function_body(func))
    return '\n\n'.join(result)


def _annotation_names(func: callable) -> set[str]:
    """Return the names of all annotations used in the function signature."""
    signature = inspect.signature(func)
    names = {
        param.annotation.__name__ for param
        in signature.parameters.values()
        if param.annotation is not inspect._empty
    }
    if signature.return_annotation is not inspect._empty:
        names.add(signature.return_annotation.__name__)
    return names


def _comment_out(source: str) -> str:
    """Comment out every line of the given source code."""
    return '\n'.join(f'#{line}' for line in source.split('\n'))


def _remove_function_body(cls: type) -> str:
    """Remove the body of the given class or function definition."""
    source_code = inspect.getsource(cls)
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            expr = node.body[0]
            if isinstance(expr, ast.Expr) and isinstance(expr.value, ast.Constant):
                node.body = [expr]  # docstring exists
            else:
                node.body = [ast.Expr(value=ast.Constant(value=...))]

    return ast.unparse(tree)
