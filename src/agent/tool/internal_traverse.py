# Copyright (c) Meta Platforms, Inc. and affiliates
import ast
import os
from typing import List, Optional, Dict, Any, Tuple

try:
    from ...dependency_analyzer.language_extensions import CODE_EXTENSIONS
except ImportError:
    from dependency_analyzer.language_extensions import CODE_EXTENSIONS

# Ordered list of extensions to probe when resolving a component path without
# an explicit extension (Python first for backward compatibility).
_PROBE_EXTENSIONS = [".py"] + [ext for ext in CODE_EXTENSIONS if ext != ".py"]


class ASTNodeAnalyzer:
    """
    Tool for analyzing AST nodes to find relationships between components in code.
    Used to identify calls (child components) and called_by (parent components).
    """

    def __init__(self, repo_path: str):
        """
        Initialize the AST Node Analyzer.

        Args:
            repo_path: Path to the repository being analyzed
        """
        self.repo_path = repo_path

    def get_component_by_path(
        self,
        ast_node,
        ast_tree,
        dependency_path: str,
        component_registry: Optional[Dict] = None,
    ) -> Optional[str]:
        """
        Universal function to get any code component (class, function, method) by its dependency path.

        Args:
            ast_node: AST node representing the focal component (None for non-Python)
            ast_tree: AST tree for the entire file (None for non-Python)
            dependency_path: Path to the dependency in format: folder1.folder2.file.component_name
                         or: folder1.folder2.file.class_name.method_name
            component_registry: Optional dict mapping component IDs to CodeComponent objects.
                                 When provided, non-Python components are resolved via line numbers.

        Returns:
            The code of the component if found, None otherwise
        """
        # Fast path for non-Python components: use stored source or line numbers
        if component_registry and dependency_path in component_registry:
            comp = component_registry[dependency_path]
            if comp.language != "python":
                if comp.source_code:
                    return comp.source_code
                return self._get_source_by_lines(comp.file_path, comp.start_line, comp.end_line)

        # Python path requires valid AST objects
        if ast_node is None or ast_tree is None:
            return None

        path_parts = dependency_path.split('.')
        if len(path_parts) < 2:
            return None

        # Determine the component type based on the path structure
        if len(path_parts) >= 3 and path_parts[-2] != 'self':
            # This could be a method: folder1.folder2.file.class_name.method_name
            last_part = path_parts[-1]
            second_last_part = path_parts[-2]

            # Check if this is likely a method
            if last_part[0].islower() and second_last_part[0].isupper():
                # This looks like a method
                return self._get_method_component(ast_node, ast_tree, dependency_path)

        # Check if this is a class (typically starts with uppercase)
        if path_parts[-1][0].isupper():
            # This looks like a class
            return self._get_class_component(ast_node, ast_tree, dependency_path)

        # Default to function (or could be a module)
        return self._get_function_component(ast_node, ast_tree, dependency_path)

    def _get_source_by_lines(self, file_path: str, start_line: int, end_line: int) -> Optional[str]:
        """
        Extract source code from a file using line numbers (used for non-Python components).

        Args:
            file_path: Absolute or repo-relative path to the file
            start_line: First line (1-indexed, inclusive)
            end_line: Last line (1-indexed, inclusive)

        Returns:
            Source code slice, or None on error
        """
        try:
            full_path = file_path if os.path.isabs(file_path) else os.path.join(self.repo_path, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if start_line < 1 or end_line < start_line:
                return None
            return ''.join(lines[start_line - 1:end_line])
        except (OSError, IndexError):
            return None
    
    def _get_class_component(self, ast_node: ast.AST, ast_tree: ast.AST, dependency_path: str) -> Optional[str]:
        """
        Get a class component by its dependency path.
        
        Args:
            ast_node: AST node representing the focal component
            ast_tree: AST tree for the entire file
            dependency_path: Path to the dependency in format: folder1.folder2.file.ClassName
            
        Returns:
            The code of the class if found, None otherwise
        """
        path_parts = dependency_path.split('.')
        class_name = path_parts[-1]
        base_name = path_parts[-2]
        folder_path = os.path.join(*path_parts[:-2]) if len(path_parts) > 2 else ''

        # Special case for 'self' which refers to the current component
        if class_name == 'self':
            if isinstance(ast_node, ast.ClassDef):
                return self._get_node_source(file_path=os.path.relpath(ast_tree.file_path, self.repo_path) if hasattr(ast_tree, 'file_path') else "", node=ast_node)
            return None

        # First check if the class is used in the current file
        local_class_info = self._find_class_init_in_node(ast_node, class_name)
        if local_class_info:
            return local_class_info

        # Try to find the file in the repository (probe all known extensions)
        full_file_path = None
        target_file_path = None
        for ext in _PROBE_EXTENSIONS:
            candidate = os.path.join(folder_path, base_name + ext)
            candidate_full = os.path.join(self.repo_path, candidate)
            if os.path.exists(candidate_full):
                full_file_path = candidate_full
                target_file_path = candidate
                break

        if full_file_path is None:
            return None

        # Parse the target file and find the class (Python only)
        try:
            with open(full_file_path, 'r') as f:
                file_content = f.read()
                target_ast = ast.parse(file_content)

            # Find the class in the target file
            for node in ast.walk(target_ast):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    return self._get_node_source(target_file_path, node)
        except Exception as e:
            return f"Error retrieving class {class_name}: {e}"

        return None
        
    def _get_function_component(self, ast_node: ast.AST, ast_tree: ast.AST, dependency_path: str) -> Optional[str]:
        """
        Get a function component by its dependency path.
        
        Args:
            ast_node: AST node representing the focal component
            ast_tree: AST tree for the entire file
            dependency_path: Path to the dependency in format: folder1.folder2.file.function_name
            
        Returns:
            The code of the function if found, None otherwise
        """
        path_parts = dependency_path.split('.')
        function_name = path_parts[-1]
        base_name = path_parts[-2]
        folder_path = os.path.join(*path_parts[:-2]) if len(path_parts) > 2 else ''

        # Special case for 'self' which refers to the current component
        if function_name == 'self':
            if isinstance(ast_node, ast.FunctionDef):
                return self._get_node_source(file_path=os.path.relpath(ast_tree.file_path, self.repo_path) if hasattr(ast_tree, 'file_path') else "", node=ast_node)
            return None

        # Try to find the file in the repository (probe all known extensions)
        full_file_path = None
        target_file_path = None
        for ext in _PROBE_EXTENSIONS:
            candidate = os.path.join(folder_path, base_name + ext)
            candidate_full = os.path.join(self.repo_path, candidate)
            if os.path.exists(candidate_full):
                full_file_path = candidate_full
                target_file_path = candidate
                break

        # If file doesn't exist, check the current file
        if full_file_path is None:
            for node in ast.walk(ast_tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    return self._get_node_source(file_path=os.path.relpath(ast_tree.file_path, self.repo_path) if hasattr(ast_tree, 'file_path') else "", node=node)
            return None

        # Parse the target file and find the function (Python only)
        try:
            with open(full_file_path, 'r') as f:
                file_content = f.read()
                target_ast = ast.parse(file_content)

            # Find the function in the target file
            for node in ast.walk(target_ast):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    return self._get_node_source(target_file_path, node)
        except Exception as e:
            return f"Error retrieving function {function_name}: {e}"

        return None
        
    def _get_method_component(self, ast_node: ast.AST, ast_tree: ast.AST, dependency_path: str) -> Optional[str]:
        """
        Get a method component by its dependency path.
        
        Args:
            ast_node: AST node representing the focal component
            ast_tree: AST tree for the entire file
            dependency_path: Path to the dependency in format: folder1.folder2.file.ClassName.method_name
            
        Returns:
            The code of the method if found, None otherwise
        """
        path_parts = dependency_path.split('.')
        if len(path_parts) < 3:  # Need at least file.class.method
            return None
            
        method_name = path_parts[-1]
        class_name = path_parts[-2]
        base_name = path_parts[-3]
        folder_path = os.path.join(*path_parts[:-3]) if len(path_parts) > 3 else ''

        # Special case for 'self' which refers to the current component
        if class_name == 'self':
            # Find the method in the current node if it's a class
            if isinstance(ast_node, ast.ClassDef):
                for item in ast_node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == method_name:
                        return self._get_node_source(file_path=os.path.relpath(ast_tree.file_path, self.repo_path) if hasattr(ast_tree, 'file_path') else "", node=item)
            return None

        # Try to find the file in the repository (probe all known extensions)
        full_file_path = None
        target_file_path = None
        for ext in _PROBE_EXTENSIONS:
            candidate = os.path.join(folder_path, base_name + ext)
            candidate_full = os.path.join(self.repo_path, candidate)
            if os.path.exists(candidate_full):
                full_file_path = candidate_full
                target_file_path = candidate
                break

        # If file doesn't exist, check the current file
        if full_file_path is None:
            for node in ast.walk(ast_tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == method_name:
                            return self._get_node_source(file_path=os.path.relpath(ast_tree.file_path, self.repo_path) if hasattr(ast_tree, 'file_path') else "", node=item)
            return None

        # Parse the target file and find the class and method (Python only)
        try:
            with open(full_file_path, 'r') as f:
                file_content = f.read()
                target_ast = ast.parse(file_content)

            # Find the class in the target file
            for node in ast.walk(target_ast):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    # Find the method in the class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == method_name:
                            return self._get_node_source(target_file_path, item)
        except Exception as e:
            return f"Error retrieving method {class_name}.{method_name}: {e}"

        return None

    def get_child_class_init(
        self, 
        ast_node: ast.AST, 
        ast_tree: ast.AST, 
        dependency_path: str
    ) -> Optional[str]:
        """
        Get the class signature and init function of a child class used by the component.
        Returns up to the end of __init__ if it exists (to save tokens).

        Args:
            ast_node: AST node representing the focal component
            ast_tree: AST tree for the entire file
            dependency_path: Path to the dependency in format: folder1.folder2.file.ClassName

        Returns:
            The code of the class initialization if found, None otherwise
        """
        class_code = self.get_component_by_path(ast_node, ast_tree, dependency_path)
        if not class_code:
            return None
            
        # Parse the class code to find the __init__ method if it exists
        try:
            class_ast = ast.parse(class_code)
            for node in ast.walk(class_ast):
                if isinstance(node, ast.ClassDef):
                    # Look for the __init__ method
                    init_method = None
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                            init_method = item
                            break
                    
                    if init_method:
                        # Get the class signature and everything up to the end of __init__
                        class_lines = class_code.split('\n')
                        init_end_line = init_method.end_lineno - node.lineno + 1
                        
                        # Ensure init_end_line doesn't exceed the total lines
                        init_end_line = min(init_end_line, len(class_lines))
                        
                        # Return class signature through the end of __init__
                        return '\n'.join(class_lines[:init_end_line])
        except:
            # If we can't parse the class code, just return it as is
            pass
            
        return class_code

    def get_child_function(
        self, 
        ast_node: ast.AST, 
        ast_tree: ast.AST, 
        dependency_path: str
    ) -> Optional[str]:
        """
        Find a function that is called by the focal component.

        Args:
            ast_node: AST node representing the focal component
            ast_tree: AST tree for the entire file
            dependency_path: Path to the dependency in format: folder1.folder2.file.function_name

        Returns:
            The code of the function if found, None otherwise
        """
        return self.get_component_by_path(ast_node, ast_tree, dependency_path)

    def get_child_method(
        self, 
        ast_node: ast.AST, 
        ast_tree: ast.AST, 
        dependency_path: str
    ) -> Optional[str]:
        """
        Find a method that is called by the focal component.

        Args:
            ast_node: AST node representing the focal component
            ast_tree: AST tree for the entire file
            dependency_path: Path to the dependency in format: folder1.folder2.file.ClassName.method_name

        Returns:
            The code of the method if found, None otherwise
        """
        return self.get_component_by_path(ast_node, ast_tree, dependency_path)

    def get_parent_components(
        self, 
        ast_node: ast.AST, 
        ast_tree: ast.AST, 
        dependency_path: str,
        dependency_graph: Optional[Dict[str, List[str]]] = None
    ) -> List[str]:
        """
        Find components that call/depend on the focal component by looking at the dependency graph.

        Args:
            ast_node: AST node representing the focal component
            ast_tree: AST tree for the entire file
            dependency_path: Path to the focal component in format: folder1.folder2.file.component_name
            dependency_graph: Optional dictionary mapping component ids to their dependencies.
                              If not provided, will only check the current file.

        Returns:
            List of code snippets of components that call/depend on the focal component
        """
        parent_components = []
        
        # If no dependency graph provided, fall back to checking just the current file
        if not dependency_graph:
            if ast_node is None or ast_tree is None:
                return parent_components

            component_name = self._get_component_name(ast_node)
            if not component_name:
                return parent_components

            # Parse the dependency path to get the file path for the current file
            path_parts = dependency_path.split('.')
            if len(path_parts) < 2:
                return parent_components

            base_name = path_parts[-2]
            folder_path = os.path.join(*path_parts[:-2]) if len(path_parts) > 2 else ''
            # Find the actual file by probing extensions
            target_file_path = os.path.join(folder_path, base_name + '.py')  # default
            for ext in _PROBE_EXTENSIONS:
                candidate = os.path.join(folder_path, base_name + ext)
                if os.path.exists(os.path.join(self.repo_path, candidate)):
                    target_file_path = candidate
                    break

            # Check for calls in the current file
            for node in ast.walk(ast_tree):
                # Skip the component itself
                if node == ast_node:
                    continue
                # Check if this is a function, async function, or class definition
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if self._contains_call_to(node, component_name):
                        parent_components.append(self._get_node_source(target_file_path, node))

            return parent_components
        
        # With dependency graph, we can find all components that depend on this component
        parent_ids = []
        for component_id, dependencies in dependency_graph.items():
            if dependency_path in dependencies:
                parent_ids.append(component_id)
        
        # Now retrieve the source code for each parent component
        for parent_id in parent_ids:
            parent_code = self.get_component_by_path(ast_node, ast_tree, parent_id)
            if parent_code:
                parent_components.append(parent_code)
        
        return parent_components
        
    def _find_class_init_in_node(self, ast_node: ast.AST, class_name: str) -> Optional[str]:
        """
        Find class instantiation in the given node.

        Args:
            ast_node: AST node to search in
            class_name: Name of the class to find

        Returns:
            The code of the class instantiation if found, None otherwise
        """
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call) and self._get_call_name(node) == class_name:
                return self._format_call_node(node)
        return None

    def _find_function_call_in_node(self, ast_node: ast.AST, function_name: str) -> bool:
        """
        Check if a function is called in the given node.

        Args:
            ast_node: AST node to search in
            function_name: Name of the function to find

        Returns:
            True if the function is called, False otherwise
        """
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call):
                call_name = self._get_call_name(node)
                if call_name == function_name:
                    return True
        return False

    def _find_method_call_in_node(
        self, 
        ast_node: ast.AST, 
        method_name: str, 
        prefix: Optional[str] = None
    ) -> bool:
        """
        Check if a method is called in the given node.

        Args:
            ast_node: AST node to search in
            method_name: Name of the method to find
            prefix: Optional prefix (object name) of the method

        Returns:
            True if the method is called, False otherwise
        """
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == method_name:
                    if prefix is None or (
                        isinstance(node.func.value, ast.Name) and node.func.value.id == prefix
                    ):
                        return True
        return False

    def _find_class_for_prefix(self, ast_tree: ast.AST, prefix: Optional[str]) -> Optional[str]:
        """
        Try to determine the class name for a given object prefix.
        This is a naive approach that checks for:
            prefix = ClassName()
        or
            prefix: ClassName

        Args:
            ast_tree: AST tree for the entire file
            prefix: The object name to find the class for

        Returns:
            Name of the class if found, None otherwise
        """
        if not prefix:
            return None

        # Look for prefix = ClassName()
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == prefix:
                        if (
                            isinstance(node.value, ast.Call)
                            and isinstance(node.value.func, ast.Name)
                        ):
                            return node.value.func.id

        # Look for prefix: ClassName
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id == prefix and isinstance(node.annotation, ast.Name):
                    return node.annotation.id

        return None

    def _get_component_name(self, ast_node: ast.AST) -> Optional[str]:
        """
        Get the name of a component (function, async function, or class).

        Args:
            ast_node: AST node representing the component

        Returns:
            Name of the component if present, None otherwise
        """
        if isinstance(ast_node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return ast_node.name
        return None

    def _contains_call_to(self, ast_node: ast.AST, component_name: str) -> bool:
        """
        Check if ast_node contains a call to the specified component name.

        Args:
            ast_node: AST node to check
            component_name: Name of the component to look for

        Returns:
            True if the node contains a call to the component, False otherwise
        """
        for node in ast.walk(ast_node):
            if isinstance(node, ast.Call):
                call_name = self._get_call_name(node)
                if call_name == component_name:
                    return True
        return False

    def _get_call_name(self, call_node: ast.Call) -> Optional[str]:
        """
        Get the name being called in a Call node.

        Args:
            call_node: AST Call node

        Returns:
            Name being called, or None if it cannot be determined
        """
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None

    def _format_call_node(self, call_node: ast.Call) -> str:
        """
        Format a call node as a string for demonstration.

        Args:
            call_node: AST Call node

        Returns:
            String representation of the call
        """
        call_name = self._get_call_name(call_node)
        return f"{call_name}(...)"

    def _get_node_source(self, file_path: str, node: ast.AST) -> str:
        """
        Get the source code for an AST node from the original file.

        Args:
            file_path: Path to the file containing the node
            node: AST node to get the source for

        Returns:
            Source code for the node, or an error message
        """
        try:
            full_path = os.path.join(self.repo_path, file_path)
            with open(full_path, 'r') as f:
                file_content = f.read()

            start_line = node.lineno
            end_line = self._get_end_line(node, file_content)
            lines = file_content.split('\n')

            # Check for docstring if this is a function or class definition
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # The docstring would be the first element in the body if it exists
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Str)):
                    # Docstring is already included in the range from lineno to end_lineno
                    pass

            # Safeguard: ensure end_line does not exceed total line count
            end_line = min(end_line, len(lines))
            return '\n'.join(lines[start_line - 1:end_line])
        except Exception as e:
            return f"Error retrieving source for {type(node).__name__}: {e}"

    def _get_end_line(self, node: ast.AST, file_content: str) -> int:
        """
        Get the end line number for an AST node, using end_lineno if present.

        Args:
            node: AST node
            file_content: Content of the file

        Returns:
            End line number of the node
        """
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno
        if hasattr(node, 'body') and node.body:
            last_subnode = node.body[-1]
            return self._get_end_line(last_subnode, file_content)
        return node.lineno