import os
from tree_sitter_language_pack import get_parser

EXT_TO_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
}


def _detect_language(file_path):
    if not file_path:
        return None
    _, ext = os.path.splitext(file_path)
    return EXT_TO_LANG.get(ext.lower())


def _node_text(source_bytes, node):
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")


def _get_name(source_bytes, node):
    name_node = node.child_by_field_name("name")
    if name_node:
        return _node_text(source_bytes, name_node)
    for child in node.children:
        if child.type in ("identifier", "property_identifier"):
            return _node_text(source_bytes, child)
    return None


def _add_var_tag(name, node, class_stack, tags):
    if not name:
        return
    tags.append({
        "name": name,
        "kind": "variable",
        "line": node.start_point[0] + 1,
        "parent": class_stack[-1] if class_stack else None
    })


def _walk_python_symbols(source_bytes, node, class_stack, tags):
    node_type = node.type
    if node_type == "class_definition":
        name = _get_name(source_bytes, node)
        if name:
            tags.append({
                "name": name,
                "kind": "class",
                "line": node.start_point[0] + 1,
                "parent": None
            })
        class_stack.append(name)
        for child in node.children:
            _walk_python_symbols(source_bytes, child, class_stack, tags)
        class_stack.pop()
        return
    if node_type == "function_definition":
        name = _get_name(source_bytes, node)
        if name:
            tags.append({
                "name": name,
                "kind": "function",
                "line": node.start_point[0] + 1,
                "parent": class_stack[-1] if class_stack else None
            })
    if node_type == "assignment":
        for child in node.children:
            if child.type == "identifier":
                _add_var_tag(_node_text(source_bytes, child), node, class_stack, tags)
    if node_type == "annotated_assignment":
        target = node.child_by_field_name("target")
        if target and target.type == "identifier":
            _add_var_tag(_node_text(source_bytes, target), node, class_stack, tags)
    if node_type == "for_statement":
        target = node.child_by_field_name("left")
        if target and target.type == "identifier":
            _add_var_tag(_node_text(source_bytes, target), node, class_stack, tags)
    if node_type == "with_statement":
        for child in node.children:
            if child.type == "as_pattern":
                alias = child.child_by_field_name("alias")
                if alias and alias.type == "identifier":
                    _add_var_tag(_node_text(source_bytes, alias), node, class_stack, tags)
    for child in node.children:
        _walk_python_symbols(source_bytes, child, class_stack, tags)


def _walk_js_symbols(source_bytes, node, class_stack, tags):
    node_type = node.type
    if node_type == "class_declaration":
        name = _get_name(source_bytes, node)
        if name:
            tags.append({
                "name": name,
                "kind": "class",
                "line": node.start_point[0] + 1,
                "parent": None
            })
        class_stack.append(name)
        for child in node.children:
            _walk_js_symbols(source_bytes, child, class_stack, tags)
        class_stack.pop()
        return
    if node_type in ("function_declaration",):
        name = _get_name(source_bytes, node)
        if name:
            tags.append({
                "name": name,
                "kind": "function",
                "line": node.start_point[0] + 1,
                "parent": None
            })
    if node_type in ("method_definition",):
        name = _get_name(source_bytes, node)
        if name:
            tags.append({
                "name": name,
                "kind": "method",
                "line": node.start_point[0] + 1,
                "parent": class_stack[-1] if class_stack else None
            })
    if node_type == "variable_declarator":
        name = _get_name(source_bytes, node)
        if name:
            tags.append({
                "name": name,
                "kind": "variable",
                "line": node.start_point[0] + 1,
                "parent": class_stack[-1] if class_stack else None
            })
    if node_type == "assignment_expression":
        left = node.child_by_field_name("left")
        if left and left.type == "identifier":
            tags.append({
                "name": _node_text(source_bytes, left),
                "kind": "variable",
                "line": node.start_point[0] + 1,
                "parent": class_stack[-1] if class_stack else None
            })
    for child in node.children:
        _walk_js_symbols(source_bytes, child, class_stack, tags)


def _walk_symbols(source_bytes, node, language, class_stack, tags):
    if language == "python":
        _walk_python_symbols(source_bytes, node, class_stack, tags)
        return
    if language in ("javascript", "typescript", "tsx"):
        _walk_js_symbols(source_bytes, node, class_stack, tags)
        return


def get_ast_map(code, file_path):
    language = _detect_language(file_path)
    if not language:
        return []
    parser = get_parser(language)
    source_bytes = code.encode("utf-8", errors="ignore")
    tree = parser.parse(source_bytes)
    tags = []
    _walk_symbols(source_bytes, tree.root_node, language, [], tags)
    return tags


def extract_context(ast_map, file_set):
    normalized_file_set = {os.path.normpath(p) for p in (file_set or [])}
    
    context = {}

    for i in normalized_file_set:
        if i in ast_map:
            context[i] = ast_map[i]
    return context