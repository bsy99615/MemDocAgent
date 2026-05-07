# Copyright (c) Meta Platforms, Inc. and affiliates
import ast
from typing import Dict, List, Optional, Set, Tuple, Union
from pathlib import Path
import os
from abc import ABC, abstractmethod

class ASTUtility(ABC):
    """Abstract base class for AST utilities."""
    
    @abstractmethod
    def _get_component_name_from_code(self, code_snippet: str) -> Optional[str]:
        """Extract component name from a code snippet.
        
        Args:
            code_snippet (str): The full code snippet of a function/method/class
            
        Returns:
            Optional[str]: The name of the component if found, None otherwise
            
        Example:
            >>> builder = CallGraphBuilder("repo_path")
            >>> builder._get_component_name_from_code("def process_data(self):\\n    return data")
            'process_data'
            >>> builder._get_component_name_from_code("class DataProcessor:\\n    def __init__(self):")
            'DataProcessor'
        """
        pass

    def _is_code_similar(self, code1: str, code2: str, threshold: float = 0.9) -> bool:
        """Check if two code snippets are similar using fuzzy matching.
        
        Args:
            code1 (str): First code snippet
            code2 (str): Second code snippet
            threshold (float): Similarity threshold (0.0 to 1.0). Default is 0.9
            
        Returns:
            bool: True if similarity score is above threshold
        """
        # Special handling for class components
        if code1.lstrip().startswith('class ') and code2.lstrip().startswith('class '):
            # For classes, just compare the class names
            class1_name = self._get_component_name_from_code(code1)
            class2_name = self._get_component_name_from_code(code2)
            return class1_name == class2_name

        # Normalize whitespace and remove empty lines
        def normalize(code: str) -> str:
            return '\n'.join(line.strip() for line in code.split('\n') if line.strip())
            
        code1_norm = normalize(code1)
        code2_norm = normalize(code2)
        
        # Simple length-based early check
        if abs(len(code1_norm) - len(code2_norm)) / max(len(code1_norm), len(code2_norm)) > (1 - threshold):
            return False
            
        # Character-based similarity score
        matches = sum(a == b for a, b in zip(code1_norm, code2_norm))
        similarity = matches / max(len(code1_norm), len(code2_norm))
        
        return similarity >= threshold

def _get_component_name_from_code(code_snippet: str) -> Optional[str]:
    """Extract component name from a code snippet.
    
    Args:
        code_snippet (str): The full code snippet of a function/method/class
        
    Returns:
        Optional[str]: The name of the component if found, None otherwise
        
    Example:
        >>> _get_component_name_from_code("def process_data(self):\\n    return data")
        'process_data'
        >>> _get_component_name_from_code("class DataProcessor:\\n    def __init__(self):")
        'DataProcessor'
    """
    # Remove leading whitespace and get first line
    first_line = code_snippet.lstrip().split('\n')[0]
    
    # Check if it's a class
    if first_line.startswith('class '):
        # Find the class name - it's between 'class ' and either '(' or ':'
        class_decl = first_line[6:].strip()  # Remove 'class ' prefix
        class_name = class_decl.split('(')[0].split(':')[0].strip()
        return class_name
        
    # Check if it's a function/method
    elif first_line.startswith('def '):
        # Find the function name - it's between 'def ' and '('
        func_decl = first_line[4:].strip()  # Remove 'def ' prefix
        func_name = func_decl.split('(')[0].strip()
        return func_name
    
    return None

class ParentNodeTransformer(ast.NodeTransformer):
    """AST transformer that adds parent references to each node."""
    def visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
        return super().visit(node)

class CallGraphBuilder(ASTUtility):
    """A class to build and analyze call graphs for Python code.
    
    This class helps analyze function calls, method calls, and class relationships
    within a Python repository.
    """
    
    def __init__(self, repo_path: str):
        """Initialize the CallGraphBuilder with a repository path.
        
        Args:
            repo_path (str): Path to the Python repository to analyze
        """
        self.repo_path = Path(repo_path)
        self.call_graph = {}
        self.class_info = {}
        self.method_info = {}
        self.function_info = {}
        self.file_asts = {}
        self._build_call_graph()
    
    def _parse_file(self, file_path: str) -> ast.AST:
        """Parse a Python file and return its AST.
        
        Args:
            file_path (str): Path to the file relative to repo_path
        """
        if file_path in self.file_asts:
            return self.file_asts[file_path]
        
        # Construct absolute path by joining repo_path with file_path
        abs_path = self.repo_path / file_path
        
        with open(abs_path) as f:
            content = f.read()
        tree = ast.parse(content)
        # Add parent references
        transformer = ParentNodeTransformer()
        tree = transformer.visit(tree)
        self.file_asts[file_path] = tree
        return tree

    def _get_signature_from_code(self, code: str, is_class: bool = False) -> str:
        """Extract signature from code.
        For functions/methods: signature ends with first ':' after first matching ')'
        For classes: signature is the class definition line ending with ':'"""
        lines = code.split('\n')
        first_line = lines[0].strip()
        
        if is_class:
            return first_line
            
        # For functions/methods
        # Find the closing parenthesis
        paren_count = 0
        end_paren_idx = -1
        for i, char in enumerate(first_line):
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    end_paren_idx = i
                    break
                    
        if end_paren_idx == -1:
            return first_line
            
        # Find the first : after the closing parenthesis
        colon_idx = first_line.find(':', end_paren_idx)
        if colon_idx == -1:
            return first_line
            
        return first_line[:colon_idx+1]

    def _get_node_code(self, file_path: str, node: ast.AST) -> str:
        """Get the source code for a node.
        
        Args:
            file_path (str): Path to the file relative to repo_path
            node (ast.AST): The AST node to get code for
        """
        abs_path = self.repo_path / file_path
        with open(abs_path) as f:
            content = f.readlines()
        return ''.join(content[node.lineno-1:node.end_lineno])

    def _is_method(self, node: ast.FunctionDef) -> bool:
        """Check if a function definition is a method."""
        parent = getattr(node, 'parent', None)
        while parent is not None:
            if isinstance(parent, ast.ClassDef):
                return True
            parent = getattr(parent, 'parent', None)
        return False

    def _build_call_graph(self):
        """Build the complete call graph for the repository."""
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if not file.endswith('.py'):
                    continue
                
                abs_file_path = Path(root) / file
                # Convert absolute path to relative path
                rel_file_path = str(abs_file_path.relative_to(self.repo_path))
                tree = self._parse_file(rel_file_path)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Store class info
                        class_code = self._get_node_code(rel_file_path, node)
                        self.class_info[(rel_file_path, class_code)] = node
                        
                        # Store method info
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                method_code = self._get_node_code(rel_file_path, item)
                                self.method_info[(rel_file_path, method_code)] = item
                                
                    elif isinstance(node, ast.FunctionDef):
                        if not self._is_method(node):
                            # Store function info
                            func_code = self._get_node_code(rel_file_path, node)
                            self.function_info[(rel_file_path, func_code)] = node

    def _get_component_name_from_code(self, code_snippet: str) -> Optional[str]:
        """Extract component name from a code snippet.
        
        Args:
            code_snippet (str): The full code snippet of a function/method/class
            
        Returns:
            Optional[str]: The name of the component if found, None otherwise
        """
        return _get_component_name_from_code(code_snippet)

    def get_child_function(self, code_component: str, file_path: str, child_function: str) -> Optional[str]:
        """Get the code of a child function that is called by the component.
        
        Args:
            code_component (str): The full code snippet of the calling component. This is used to
                                uniquely identify the component in case of name collisions.
            file_path (str): Path to the file containing the component
            child_function (str): Name of the function being called
            
        Returns:
            Optional[str]: The code of the child function if found, None otherwise
            
        Example:
            >>> builder = CallGraphBuilder("repo_path")
            >>> builder.get_child_function(
            ...     "def main_function():\\n    result = utility_function()\\n    return result",
            ...     "main.py",
            ...     "utility_function"
            ... )
            'def utility_function():\\n    return "utility"'
        """
        tree = self._parse_file(file_path)
        target_node = None
        
        component_name = self._get_component_name_from_code(code_component)
        if not component_name:
            return None
        
        # Find the target node
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == component_name:
                # Get the code of this node and verify it matches using fuzzy matching
                node_code = self._get_node_code(file_path, node)
                if self._is_code_similar(node_code, code_component):
                    target_node = node
                    break
        
        if not target_node:
            return None
            
        # Look for calls to the child function
        for node in ast.walk(target_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == child_function:
                    # Find the function definition
                    for func_file, func_code in self.function_info:
                        func_node = self.function_info[(func_file, func_code)]
                        if func_node.name == child_function:
                            return func_code
        return None

    def _resolve_instance_type(self, node: ast.AST, instance_name: str) -> Optional[str]:
        """Resolve the class type of an instance variable by looking at assignments.
        
        Args:
            node: The AST node to start searching from (usually a function/method)
            instance_name: The name of the instance variable to resolve
            
        Returns:
            Optional[str]: The name of the class if found, None otherwise
        """
        # First check local assignments in the current function/method
        for n in ast.walk(node):
            if isinstance(n, ast.Assign):
                for target in n.targets:
                    if isinstance(target, ast.Name) and target.id == instance_name:
                        if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name):
                            return n.value.func.id
                            
        # If not found locally and we're in a method, check class __init__
        if isinstance(node, ast.FunctionDef):
            class_node = self._get_class_node(node)
            if class_node:
                for method in class_node.body:
                    if isinstance(method, ast.FunctionDef) and method.name == '__init__':
                        for n in ast.walk(method):
                            if isinstance(n, ast.Assign):
                                for target in n.targets:
                                    if isinstance(target, ast.Attribute) and \
                                       isinstance(target.value, ast.Name) and \
                                       target.value.id == 'self' and \
                                       target.attr == instance_name and \
                                       isinstance(n.value, ast.Call) and \
                                       isinstance(n.value.func, ast.Name):
                                        return n.value.func.id
        return None

    def _get_class_node(self, method_node: ast.FunctionDef) -> Optional[ast.ClassDef]:
        """Get the ClassDef node that contains this method."""
        parent = getattr(method_node, 'parent', None)
        while parent is not None:
            if isinstance(parent, ast.ClassDef):
                return parent
            parent = getattr(parent, 'parent', None)
        return None

    def get_child_method(self, code_component: str, file_path: str, 
                        method_name: str, prefix: Optional[str] = None, find_all: bool = False) -> Union[Optional[str], Dict[str, str]]:
        """Get the code of a child method that is called by the component.
        
        Args:
            code_component (str): The full code snippet of the calling component. This is used to
                                uniquely identify the component in case of name collisions.
            file_path (str): Path to the file containing the component
            method_name (str): Name of the method being called
            prefix (Optional[str]): Optional prefix before method name (e.g., 'self', instance name, or class name)
            find_all (bool): Whether to find all methods with this name across classes
            
        Returns:
            If find_all=False:
                Optional[str]: The code of the child method if found, None otherwise
            If find_all=True:
                Dict[str, str]: Dictionary mapping class names to method code for all matching methods
                
        Note:
            This method handles three types of method calls:
            1. self.method() - method in same class
            2. ClassName.method() - direct class method call
            3. instance.method() - method call through instance variable
            
            If prefix is provided:
            - If prefix is 'self': looks for method in the same class
            - If prefix starts with uppercase: treats it as a class name
            - If prefix starts with lowercase: treats it as an instance variable
        """
        tree = self._parse_file(file_path)
        target_node = None
        
        component_name = self._get_component_name_from_code(code_component)
        if not component_name:
            return {} if find_all else None
        
        # Find the target node
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == component_name:
                # Get the code of this node and verify it matches using fuzzy matching
                node_code = self._get_node_code(file_path, node)
                if self._is_code_similar(node_code, code_component):
                    target_node = node
                    break
        
        if not target_node:
            return {} if find_all else None

        if find_all:
            # Find all methods with this name across all classes
            results = {}
            for method_file, method_code in self.method_info:
                method_node = self.method_info[(method_file, method_code)]
                if method_node.name == method_name:
                    class_node = self._get_class_node(method_node)
                    if class_node:
                        results[class_node.name] = method_code
            return results
            
        # If prefix is provided, use it to narrow down the search
        if prefix is not None:
            target_class = None
            
            if prefix == 'self':
                # Case 1: self.method()
                target_class = self._get_class_of_method(target_node)
            elif prefix[0].isupper():
                # Case 2: ClassName.method()
                target_class = prefix
            else:
                # Case 3: instance.method()
                target_class = self._resolve_instance_type(target_node, prefix)
                
            if target_class:
                for method_file, method_code in self.method_info:
                    method_node = self.method_info[(method_file, method_code)]
                    if method_node.name == method_name:
                        # Verify this method belongs to the target class
                        method_class = self._get_class_of_method(method_node)
                        if method_class == target_class:
                            return method_code
                return None
            
        # If no prefix or target class not found, fall back to original behavior
        # Look for method calls
        for node in ast.walk(target_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == method_name:
                    target_class = None
                    
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'self':
                            # Case 1: self.method()
                            target_class = self._get_class_of_method(target_node)
                        else:
                            # Case 2: ClassName.method() or Case 3: instance.method()
                            # Try as class name first
                            for class_file, class_code in self.class_info:
                                class_node = self.class_info[(class_file, class_code)]
                                if class_node.name == node.func.value.id:
                                    target_class = class_node.name
                                    break
                            
                            # If not found as class name, try as instance variable
                            if not target_class:
                                target_class = self._resolve_instance_type(target_node, node.func.value.id)
                    
                    elif isinstance(node.func.value, ast.Attribute):
                        # Handle nested attributes like self.processor.process()
                        if isinstance(node.func.value.value, ast.Name):
                            if node.func.value.value.id == 'self':
                                # Get type of self.processor
                                instance_var = node.func.value.attr
                                target_class = self._resolve_instance_type(target_node, instance_var)
                    
                    # If we found the target class, find the method
                    if target_class:
                        for method_file, method_code in self.method_info:
                            method_node = self.method_info[(method_file, method_code)]
                            if method_node.name == method_name:
                                # Verify this method belongs to the target class
                                method_class = self._get_class_of_method(method_node)
                                if method_class == target_class:
                                    return method_code
        return None

    def get_child_class(self, code_component: str, file_path: str, child_class: str) -> Optional[str]:
        """Get the class signature and init function of a child class used by the component.
        
        Args:
            code_component (str): The full code snippet of the calling component. This is used to
                                uniquely identify the component in case of name collisions.
            file_path (str): Path to the file containing the calling component
            child_class (str): Name of the class being used
            
        Returns:
            Optional[str]: The code of the child class and its __init__ if found, None otherwise
            
        Example:
            >>> builder = CallGraphBuilder("repo_path")
            >>> builder.get_child_class(
            ...     "def main_function():\\n    helper = HelperClass()\\n    return helper.data",
            ...     "main.py",
            ...     "HelperClass"
            ... )
            'class HelperClass:\\n    def __init__(self):\\n        self.data = []'
        """
        tree = self._parse_file(file_path)
        target_node = None
        
        component_name = self._get_component_name_from_code(code_component)
        if not component_name:
            return None
        
        # Find the target node
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == component_name:
                # Get the code of this node and verify it matches using fuzzy matching
                node_code = self._get_node_code(file_path, node)
                if self._is_code_similar(node_code, code_component):
                    target_node = node
                    break
        
        if not target_node:
            return None
            
        # Look for class usage
        for node in ast.walk(target_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == child_class:
                    # Find the class definition
                    for class_file, class_code in self.class_info:
                        class_node = self.class_info[(class_file, class_code)]
                        if class_node.name == child_class:
                            # Get class signature and __init__
                            init_method = None
                            for item in class_node.body:
                                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                                    init_method = self._get_node_code(class_file, item)
                                    break
                            if init_method:
                                return f"{class_code}\n{init_method}"
                            return class_code
        return None

    def get_child_class_init(self, code_component: str, file_path: str, child_class: str) -> Optional[str]:
        """Get the class signature and init function of a child class used by the component.
        Similar to get_child_class but only returns up to the end of __init__ if it exists.
        
        Args:
            code_component (str): The full code snippet of the calling component. This is used to
                                uniquely identify the component in case of name collisions.
            file_path (str): Path to the file containing the calling component
            child_class (str): Name of the class being used
            
        Returns:
            Optional[str]: The code of the child class up to the end of __init__ if found,
                         or the full class code if __init__ doesn't exist, None if class not found
            
        Example:
            >>> builder = CallGraphBuilder("repo_path")
            >>> builder.get_child_class_init(
            ...     "def main_function():\\n    helper = HelperClass()\\n    return helper.data",
            ...     "main.py",
            ...     "HelperClass"
            ... )
            'class HelperClass:\\n    def __init__(self):\\n        self.data = []'
        """
        # Get the full class code first using existing method
        full_code = self.get_child_class(code_component, file_path, child_class)
        if not full_code:
            return None
            
        # Split into lines for analysis
        lines = full_code.split('\n')
        
        # Find the __init__ method
        init_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('def __init__'):
                init_start = i
                break
                
        # If no __init__, return full code
        if init_start == -1:
            return full_code
            
        # Find the next method definition after __init__
        next_method_start = -1
        for i, line in enumerate(lines[init_start + 1:], start=init_start + 1):
            if line.strip().startswith('def '):
                next_method_start = i
                break
                
        # If no next method found, return up to the end
        if next_method_start == -1:
            return full_code
            
        # Return code up to the start of next method
        return '\n'.join(lines[:next_method_start])

    def _get_class_of_method(self, method_node: ast.FunctionDef) -> Optional[str]:
        """Get the name of the class that contains this method."""
        parent = getattr(method_node, 'parent', None)
        while parent is not None:
            if isinstance(parent, ast.ClassDef):
                return parent.name
            parent = getattr(parent, 'parent', None)
        return None

    def get_parent(self, code_component: str, file_path: str, class_name: Optional[str] = None) -> List[str]:
        """Get the code of any components that use the focal component.
        
        Args:
            code_component: String representation of the component
            file_path: Path to the file containing the component
            class_name: If the component is a method, specify its class name to avoid
                     false matches with methods of same name in other classes
            
        Returns:
            List[str]: List of code blocks of parent components that use this component
        """
        results = []
        
        component_name = self._get_component_name_from_code(code_component)
        if not component_name:
            return []
        
        
        tree = self._parse_file(file_path)
        found_target = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == component_name:
                node_code = self._get_node_code(file_path, node)
                if self._is_code_similar(node_code, code_component):
                    found_target = True
                    break
        
        if not found_target:
            return []
        
        # Check functions
        for func_file, func_code in self.function_info:
            func_node = self.function_info[(func_file, func_code)]
            # Check if this function calls our component
            for node in ast.walk(func_node):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == component_name:
                        results.append(func_code)
                        break  # Found usage in this function, move to next
                    
        # Check methods
        for method_file, method_code in self.method_info:
            method_node = self.method_info[(method_file, method_code)]
            # Skip __init__ methods
            if method_node.name == '__init__':
                continue
            # Check if this method calls our component
            for node in ast.walk(method_node):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and node.func.attr == component_name:
                        # If class_name is specified, verify the method belongs to that class
                        if class_name:
                            # Get the class of the target method
                            target_class = None
                            if isinstance(node.func.value, ast.Name):
                                # For self.method() calls
                                if node.func.value.id == 'self':
                                    target_class = self._get_class_of_method(method_node)
                                # For ClassName.method() calls
                                else:
                                    target_class = node.func.value.id
                            # For instance.method() calls through instance variables
                            elif isinstance(node.func.value, ast.Attribute):
                                # Try to find the instance variable in __init__
                                method_class = self._get_class_of_method(method_node)
                                if method_class:
                                    # Look up the class definition
                                    for class_file, class_code in self.class_info:
                                        class_node = self.class_info[(class_file, class_code)]
                                        if class_node.name == method_class:
                                            # Find __init__ method
                                            for init_node in class_node.body:
                                                if isinstance(init_node, ast.FunctionDef) and init_node.name == '__init__':
                                                    # Look for assignments to this instance variable
                                                    instance_var = node.func.value.value.id  # e.g., 'self' from self.data_processor
                                                    var_name = node.func.value.attr  # e.g., 'data_processor' from self.data_processor
                                                    if instance_var == 'self':
                                                        for n in ast.walk(init_node):
                                                            if isinstance(n, ast.Assign):
                                                                for target in n.targets:
                                                                    if isinstance(target, ast.Attribute) and \
                                                                       isinstance(target.value, ast.Name) and \
                                                                       target.value.id == 'self' and \
                                                                       target.attr == var_name and \
                                                                       isinstance(n.value, ast.Call):
                                                                        # Found the initialization
                                                                        if isinstance(n.value.func, ast.Name):
                                                                            target_class = n.value.func.id
                                                                            break
                            if target_class == class_name:
                                results.append(method_code)
                        else:
                            results.append(method_code)
                        break  # Found usage in this method, move to next
                    elif isinstance(node.func, ast.Name) and node.func.id == component_name:
                        results.append(method_code)
                        break  # Found usage in this method, move to next
                        
        # Check class __init__ methods
        for class_file, class_code in self.class_info:
            class_node = self.class_info[(class_file, class_code)]
            # Look for __init__ method
            for node in class_node.body:
                if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                    # Check if __init__ uses our component
                    for call_node in ast.walk(node):
                        if isinstance(call_node, ast.Call):
                            if isinstance(call_node.func, ast.Name) and call_node.func.id == component_name:
                                # Get class signature and init method
                                class_sig = self._get_node_code(class_file, class_node).split('\n')[0]
                                init_code = self._get_node_code(class_file, node)
                                results.append(f"{class_sig}\n{init_code}")
                                break  # Found usage in this class, move to next
                                
        return results 

# Add this new class after the CallGraphBuilder class
class ASTNodeAnalyzer:
    """A class to analyze AST nodes directly without string matching.
    
    This class works directly with AST nodes to analyze function calls, method calls,
    and class relationships within a Python repository, avoiding the need to re-parse
    files that have already been parsed.
    """
    
    def __init__(self, repo_path: str):
        """Initialize the ASTNodeAnalyzer with a repository path.
        
        Args:
            repo_path (str): Path to the Python repository to analyze
        """
        self.repo_path = Path(repo_path)
        # Reference to an existing CallGraphBuilder to reuse the pre-built info
        self.call_graph_builder = CallGraphBuilder(repo_path)
        
    def get_child_function(self, focal_node: ast.AST, file_tree: ast.AST, 
                          file_path: str, child_function: str) -> Optional[str]:
        """Get the code of a child function that is called by the component.
        
        Args:
            focal_node: The AST node representing the focal component
            file_tree: The AST tree for the entire file
            file_path: Path to the file containing the component
            child_function: Name of the function being called
            
        Returns:
            Optional[str]: The code of the child function if found, None otherwise
        """
        # Look for calls to the child function in the focal node
        for node in ast.walk(focal_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == child_function:
                    # Find the function definition in the function_info dictionary
                    for func_file, func_code in self.call_graph_builder.function_info:
                        func_node = self.call_graph_builder.function_info[(func_file, func_code)]
                        if func_node.name == child_function:
                            return func_code
        return None
    
    def get_child_method(self, focal_node: ast.AST, file_tree: ast.AST,
                        file_path: str, method_name: str,
                        prefix: Optional[str] = None,
                        find_all: bool = False) -> Union[Optional[str], Dict[str, str]]:
        """Get the code of a child method that is called by the component.
        
        Args:
            focal_node: The AST node representing the focal component
            file_tree: The AST tree for the entire file
            file_path: Path to the file containing the component
            method_name: Name of the method being called
            prefix: Optional prefix before method name (e.g., 'self', instance name, or class name)
            find_all: Whether to find all methods with this name across classes
            
        Returns:
            If find_all=False:
                Optional[str]: The code of the child method if found, None otherwise
            If find_all=True:
                Dict[str, str]: Dictionary mapping class names to method code for all matching methods
        """
        if find_all:
            # Find all methods with this name across all classes
            results = {}
            for method_file, method_code in self.call_graph_builder.method_info:
                method_node = self.call_graph_builder.method_info[(method_file, method_code)]
                if method_node.name == method_name:
                    class_node = self.call_graph_builder._get_class_node(method_node)
                    if class_node:
                        results[class_node.name] = method_code
            return results
        
        # If prefix is provided, use it to narrow down the search
        if prefix is not None:
            target_class = None
            
            if prefix == 'self':
                # Case 1: self.method()
                target_class = self.call_graph_builder._get_class_of_method(focal_node)
            elif prefix[0].isupper():
                # Case 2: ClassName.method()
                target_class = prefix
            else:
                # Case 3: instance.method()
                target_class = self.call_graph_builder._resolve_instance_type(focal_node, prefix)
                
            if target_class:
                for method_file, method_code in self.call_graph_builder.method_info:
                    method_node = self.call_graph_builder.method_info[(method_file, method_code)]
                    if method_node.name == method_name:
                        # Verify this method belongs to the target class
                        method_class = self.call_graph_builder._get_class_of_method(method_node)
                        if method_class == target_class:
                            return method_code
                return None
        
        # If no prefix or target class not found, fall back to searching in the AST
        for node in ast.walk(focal_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == method_name:
                    target_class = None
                    
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'self':
                            # Case 1: self.method()
                            target_class = self.call_graph_builder._get_class_of_method(focal_node)
                        else:
                            # Case 2: ClassName.method() or Case 3: instance.method()
                            # Try as class name first
                            for class_file, class_code in self.call_graph_builder.class_info:
                                class_node = self.call_graph_builder.class_info[(class_file, class_code)]
                                if class_node.name == node.func.value.id:
                                    target_class = class_node.name
                                    break
                            
                            # If not found as class name, try as instance variable
                            if not target_class:
                                target_class = self.call_graph_builder._resolve_instance_type(focal_node, node.func.value.id)
                    
                    elif isinstance(node.func.value, ast.Attribute):
                        # Handle nested attributes like self.processor.process()
                        if isinstance(node.func.value.value, ast.Name):
                            if node.func.value.value.id == 'self':
                                # Get type of self.processor
                                instance_var = node.func.value.attr
                                target_class = self.call_graph_builder._resolve_instance_type(focal_node, instance_var)
                    
                    # If we found the target class, find the method
                    if target_class:
                        for method_file, method_code in self.call_graph_builder.method_info:
                            method_node = self.call_graph_builder.method_info[(method_file, method_code)]
                            if method_node.name == method_name:
                                # Verify this method belongs to the target class
                                method_class = self.call_graph_builder._get_class_of_method(method_node)
                                if method_class == target_class:
                                    return method_code
        return None
    
    def get_child_class_init(self, focal_node: ast.AST, file_tree: ast.AST,
                            file_path: str, child_class: str) -> Optional[str]:
        """Get the class signature and init function of a child class used by the component.
        
        Args:
            focal_node: The AST node representing the focal component
            file_tree: The AST tree for the entire file
            file_path: Path to the file containing the component
            child_class: Name of the class being used
            
        Returns:
            Optional[str]: The code of the child class up to the end of __init__ if found,
                         or the full class code if __init__ doesn't exist, None if class not found
        """
        # Look for calls to the child class in the focal node
        for node in ast.walk(focal_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == child_class:
                    # Find the class definition
                    for class_file, class_code in self.call_graph_builder.class_info:
                        class_node = self.call_graph_builder.class_info[(class_file, class_code)]
                        if class_node.name == child_class:
                            # Get class signature and __init__
                            init_method = None
                            for item in class_node.body:
                                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                                    init_method = self.call_graph_builder._get_node_code(class_file, item)
                                    break
                            
                            if init_method:
                                return f"{class_code}\n{init_method}"
                            return class_code
        return None
    
    def get_parent_components(self, focal_node: ast.AST, file_tree: ast.AST,
                             file_path: str, class_name: Optional[str] = None) -> List[str]:
        """Get the code of any components that use the focal component.
        
        Args:
            focal_node: The AST node representing the focal component
            file_tree: The AST tree for the entire file
            file_path: Path to the file containing the component
            class_name: If the component is a method, specify its class name to avoid
                     false matches with methods of same name in other classes
            
        Returns:
            List[str]: List of code blocks of parent components that use the focal component
        """
        # Check what type of node this is
        component_name = None
        if isinstance(focal_node, ast.FunctionDef):
            component_name = focal_node.name
        elif isinstance(focal_node, ast.ClassDef):
            component_name = focal_node.name
        else:
            return []
            
        # Get the source code of the focal node
        focal_code = self.call_graph_builder._get_node_code(file_path, focal_node)
        
        # Now use the existing implementation from CallGraphBuilder
        return self.call_graph_builder.get_parent(focal_code, file_path, class_name) 