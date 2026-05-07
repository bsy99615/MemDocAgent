# Copyright (c) Meta Platforms, Inc. and affiliates
"""
AST-based Python code parser that extracts dependency information between code components.

This module identifies imports and references between Python code components (functions, classes, methods)
and builds a dependency graph for topological sorting.
"""

import ast
import os
import json
import logging
import builtins
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from pathlib import Path

from .language_extensions import CODE_EXTENSIONS

logger = logging.getLogger(__name__)

# Built-in Python types and modules that should be excluded from dependencies
BUILTIN_TYPES = {name for name in dir(builtins)}
STANDARD_MODULES = {
    'abc', 'argparse', 'array', 'asyncio', 'base64', 'collections', 'copy', 
    'csv', 'datetime', 'enum', 'functools', 'glob', 'io', 'itertools', 
    'json', 'logging', 'math', 'os', 'pathlib', 'random', 're', 'shutil', 
    'string', 'sys', 'time', 'typing', 'uuid', 'warnings', 'xml'
}
EXCLUDED_NAMES = {'self', 'cls'}

@dataclass
class CodeComponent:
    """
    Represents a single code component (function, class, or method) in a codebase.

    Stores the component's identifier, AST node, dependencies, and other metadata.
    Supports Python (via ast module) and other languages (via tree-sitter analyzers).
    """
    # Unique identifier for the component, format: module_path.ClassName.method_name
    id: str

    # AST node representing this component (Python only; None for other languages)
    node: Optional[Any]

    # Type of component: 'class', 'function', or 'method'
    component_type: str

    # Full path to the file containing this component
    file_path: str

    # Relative path within the repo
    relative_path: str

    # Set of component IDs this component depends on
    depends_on: Set[str] = field(default_factory=set)

    # Original source code of the component
    source_code: Optional[str] = None

    # Line numbers in the file (1-indexed)
    start_line: int = 0
    end_line: int = 0

    # Whether the component already has a docstring
    has_docstring: bool = False

    # Content of the docstring if it exists, empty string otherwise
    docstring: str = ""

    # Programming language of this component (e.g. "python", "java", "javascript")
    language: str = "python"

    # Function/method parameter names (populated by tree-sitter analyzers)
    parameters: Optional[List[str]] = None

    # Parent class names for inheritance (populated by tree-sitter analyzers)
    base_classes: Optional[List[str]] = None

    # Containing class name for methods (populated by tree-sitter analyzers)
    class_name: Optional[str] = None

    # Formatted import block for the file containing this component (Python only; not persisted)
    imports: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert this component to a dictionary representation for JSON serialization."""
        return {
            'id': self.id,
            'component_type': self.component_type,
            'file_path': self.file_path,
            'relative_path': self.relative_path,
            'depends_on': list(self.depends_on),
            'start_line': self.start_line,
            'end_line': self.end_line,
            'has_docstring': self.has_docstring,
            'docstring': self.docstring,
            'language': self.language,
            'parameters': self.parameters,
            'base_classes': self.base_classes,
            'class_name': self.class_name,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CodeComponent':
        """Create a CodeComponent from a dictionary representation."""
        component = CodeComponent(
            id=data['id'],
            node=None,  # AST node is not serialized
            component_type=data['component_type'],
            file_path=data['file_path'],
            relative_path=data['relative_path'],
            depends_on=set(data.get('depends_on', [])),
            start_line=data.get('start_line', 0),
            end_line=data.get('end_line', 0),
            has_docstring=data.get('has_docstring', False),
            docstring=data.get('docstring', ""),
            language=data.get('language', 'python'),
            parameters=data.get('parameters'),
            base_classes=data.get('base_classes'),
            class_name=data.get('class_name'),
        )
        return component


class ImportCollector(ast.NodeVisitor):
    """Collects import statements from Python code."""
    
    def __init__(self):
        self.imports = set()
        self.from_imports = {}  # module -> [names]
        
    def visit_Import(self, node: ast.Import):
        """Process 'import x' statements."""
        for name in node.names:
            self.imports.add(name.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Process 'from x import y' statements."""
        if node.module is not None:
            module = node.module
            if module not in self.from_imports:
                self.from_imports[module] = []
            
            for name in node.names:
                if name.name != '*':
                    self.from_imports[module].append(name.name)
        
        self.generic_visit(node)


class MethodDependencyCollector(ast.NodeVisitor):
    """
    Special dependency collector for methods that also tracks 'self.XXX' references
    as potential dependencies.
    """
    
    def __init__(self, class_id: str, method_id: str, class_methods: Dict[str, str]):
        self.class_id = class_id
        self.method_id = method_id
        self.class_methods = class_methods  # method_name -> full_method_id
        self.self_attr_refs = set()  # Set of attributes accessed via self.XXX
        
    def visit_Attribute(self, node: ast.Attribute):
        """Process attribute access, specifically looking for self.XXX references."""
        if (isinstance(node.value, ast.Name) and 
            node.value.id == 'self' and 
            isinstance(node.ctx, ast.Load)):
            
            # Found a self.XXX reference
            attr_name = node.attr
            self.self_attr_refs.add(attr_name)
        
        self.generic_visit(node)
    
    def get_method_dependencies(self) -> Set[str]:
        """
        Get the set of methods that this method depends on based on self.XXX references.
        
        Returns:
            A set of method IDs that this method depends on
        """
        dependencies = set()
        
        # Check if any self.attr references match method names
        for attr in self.self_attr_refs:
            if attr in self.class_methods:
                # This is a reference to another method in the class
                dependencies.add(self.class_methods[attr])
        
        return dependencies


class DependencyCollector(ast.NodeVisitor):
    """
    Collects dependencies between code components by analyzing
    attribute access, function calls, and class references.
    """
    
    def __init__(self, imports, from_imports, current_module, repo_modules):
        self.imports = imports
        self.from_imports = from_imports
        self.current_module = current_module
        self.repo_modules = repo_modules
        self.dependencies = set()
        self._current_class = None
        # Track local variables defined in the current context
        self.local_variables = set()
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Process class definitions."""
        old_class = self._current_class
        self._current_class = node.name
        
        # Check for base classes dependencies
        for base in node.bases:
            if isinstance(base, ast.Name):
                # Simple name reference, could be an imported class
                self._add_dependency(base.id)
            elif isinstance(base, ast.Attribute):
                # Module.Class reference
                self._process_attribute(base)
        
        self.generic_visit(node)
        self._current_class = old_class
    
    def visit_Assign(self, node: ast.Assign):
        """Track local variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Add to local variables
                self.local_variables.add(target.id)
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        """Process function calls."""
        if isinstance(node.func, ast.Name):
            # Direct function call
            self._add_dependency(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            # Method call or module.function call
            self._process_attribute(node.func)
        
        self.generic_visit(node)
    
    def visit_Name(self, node: ast.Name):
        """Process name references."""
        if isinstance(node.ctx, ast.Load):
            self._add_dependency(node.id)
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute):
        """Process attribute access."""
        self._process_attribute(node)
        self.generic_visit(node)
    
    def _process_attribute(self, node: ast.Attribute):
        """Process an attribute node to extract potential dependencies."""
        parts = []
        current = node
        
        # Traverse the attribute chain (e.g., module.submodule.Class.method)
        while isinstance(current, ast.Attribute):
            parts.insert(0, current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.insert(0, current.id)
            
            # Skip if the first part is a local variable
            if parts[0] in self.local_variables:
                return
                
            # Skip if the first part is in our excluded names
            if parts[0] in EXCLUDED_NAMES:
                return
                
            # Check if the first part is an imported module
            if parts[0] in self.imports:
                module_path = parts[0]
                # Skip standard library modules
                if module_path in STANDARD_MODULES:
                    return
                    
                # If it's a repo module, add as dependency
                if module_path in self.repo_modules:
                    if len(parts) > 1:
                        # Example: module.Class or module.function
                        self.dependencies.add(f"{module_path}.{parts[1]}")
            
            # Check from imports
            elif parts[0] in self.from_imports.keys():
                # Skip standard library modules
                if parts[0] in STANDARD_MODULES:
                    return
                    
                # Check if the name is in the imported names
                if len(parts) > 1 and parts[1] in self.from_imports[parts[0]]:
                    self.dependencies.add(f"{parts[0]}.{parts[1]}")
    
    def _add_dependency(self, name):
        """Add a potential dependency based on a name reference."""
        # Skip built-in types
        if name in BUILTIN_TYPES:
            return
            
        # Skip excluded names
        if name in EXCLUDED_NAMES:
            return
            
        # Skip local variables
        if name in self.local_variables:
            return
            
        # Check if name is directly imported from a module
        for module, imported_names in self.from_imports.items():
            # Skip standard library modules
            if module in STANDARD_MODULES:
                continue
                
            if name in imported_names and module in self.repo_modules:
                self.dependencies.add(f"{module}.{name}")
                return
                
        # Check if name refers to a component in the current module
        local_component_id = f"{self.current_module}.{name}"
        self.dependencies.add(local_component_id)


def add_parent_to_nodes(tree: ast.AST) -> None:
    """
    Add a 'parent' attribute to each node in the AST.
    
    Args:
        tree: The AST to process
    """
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node


class DependencyParser:
    """
    Parses Python code to build a dependency graph between code components.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.components: Dict[str, CodeComponent] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.modules: Set[str] = set()
        
    def parse_repository(self):
        """
        Parse all supported source files in the repository to build the dependency graph.

        Python files are processed with the built-in ast module (3-pass analysis).
        Other languages are processed via tree-sitter based analyzers.
        """
        logger.info(f"Parsing repository at {self.repo_path}")

        # First pass: collect all modules and code components
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                ext = Path(file).suffix.lower()
                language = CODE_EXTENSIONS.get(ext)
                if language is None:
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.repo_path)

                if language == "python":
                    # Use existing Python AST pipeline
                    module_path = self._file_to_module_path(relative_path)
                    self.modules.add(module_path)
                    self._parse_file(file_path, relative_path, module_path)
                else:
                    # Use tree-sitter based analyzer for other languages
                    self._parse_file_with_treesitter(file_path, relative_path, language)

        # Second pass: resolve Python dependencies
        self._resolve_dependencies()

        # Third pass: add class dependencies on methods
        self._add_class_method_dependencies()

        # Build dependency_graph from components' depends_on
        self.dependency_graph = {
            comp_id: list(component.depends_on)
            for comp_id, component in self.components.items()
        }

        logger.info(f"Found {len(self.components)} code components")
        return self.components
    
    def _file_to_module_path(self, file_path: str) -> str:
        """Convert a file path to a Python module path."""
        # Remove .py extension and convert / to .
        path = file_path[:-3] if file_path.endswith(".py") else file_path
        return path.replace(os.path.sep, ".")
    
    def _parse_file(self, file_path: str, relative_path: str, module_path: str):
        """Parse a single Python file to collect code components."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            # Add parent field to AST nodes for easier traversal
            add_parent_to_nodes(tree)
            
            # Collect imports
            import_collector = ImportCollector()
            import_collector.visit(tree)
            
            # Collect code components
            imports_str = self._format_imports(import_collector.imports, import_collector.from_imports)
            self._collect_components(tree, file_path, relative_path, module_path, source, imports_str)
            
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.warning(f"Error parsing {file_path}: {e}")
    
    def _collect_components(self, tree: ast.AST, file_path: str, relative_path: str,
                          module_path: str, source: str, imports_str: Optional[str] = None):
        """Collect all code components (functions, classes, methods) from an AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Class definition
                class_id = f"{module_path}.{node.name}"
                
                # Check if the class has a docstring
                has_docstring = (
                    len(node.body) > 0 
                    and isinstance(node.body[0], ast.Expr) 
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                )
                
                # Extract docstring if it exists
                docstring = self._get_docstring(source, node) if has_docstring else ""
                
                component = CodeComponent(
                    id=class_id,
                    node=node,
                    component_type="class",
                    file_path=file_path,
                    relative_path=relative_path,
                    source_code=self._get_source_segment(source, node),
                    start_line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    has_docstring=has_docstring,
                    docstring=docstring,
                    imports=imports_str,
                )
                
                self.components[class_id] = component
                
                # Collect methods within the class
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_id = f"{class_id}.{item.name}"
                        
                        # Check if the method has a docstring
                        method_has_docstring = (
                            len(item.body) > 0 
                            and isinstance(item.body[0], ast.Expr) 
                            and isinstance(item.body[0].value, ast.Constant)
                            and isinstance(item.body[0].value.value, str)
                        )
                        
                        # Extract docstring if it exists
                        method_docstring = self._get_docstring(source, item) if method_has_docstring else ""
                        
                        method_component = CodeComponent(
                            id=method_id,
                            node=item,
                            component_type="method",
                            file_path=file_path,
                            relative_path=relative_path,
                            source_code=self._get_source_segment(source, item),
                            start_line=item.lineno,
                            end_line=getattr(item, "end_lineno", item.lineno),
                            has_docstring=method_has_docstring,
                            docstring=method_docstring,
                            imports=imports_str,
                        )
                        
                        self.components[method_id] = method_component
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Only collect top-level functions
                if hasattr(node, 'parent') and isinstance(node.parent, ast.Module):
                    func_id = f"{module_path}.{node.name}"
                    
                    # Check if the function has a docstring
                    has_docstring = (
                        len(node.body) > 0 
                        and isinstance(node.body[0], ast.Expr) 
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    )
                    
                    # Extract docstring if it exists
                    docstring = self._get_docstring(source, node) if has_docstring else ""
                    
                    component = CodeComponent(
                        id=func_id,
                        node=node,
                        component_type="function",
                        file_path=file_path,
                        relative_path=relative_path,
                        source_code=self._get_source_segment(source, node),
                        start_line=node.lineno,
                        end_line=getattr(node, "end_lineno", node.lineno),
                        has_docstring=has_docstring,
                        docstring=docstring,
                        imports=imports_str,
                    )
                    
                    self.components[func_id] = component
    
    def _get_treesitter_analyzer(self, language: str):
        """Return the analyze_<language>_file function, or None if not available."""
        try:
            if language == "javascript":
                from .analyzers.javascript import analyze_javascript_file_treesitter as fn
                return fn
            elif language == "typescript":
                from .analyzers.typescript import analyze_typescript_file_treesitter as fn
                return fn
            elif language == "java":
                from .analyzers.java import analyze_java_file as fn
                return fn
            elif language == "kotlin":
                from .analyzers.kotlin import analyze_kotlin_file as fn
                return fn
            elif language == "csharp":
                from .analyzers.csharp import analyze_csharp_file as fn
                return fn
            elif language == "c":
                from .analyzers.c import analyze_c_file as fn
                return fn
            elif language == "cpp":
                from .analyzers.cpp import analyze_cpp_file as fn
                return fn
            elif language == "php":
                from .analyzers.php import analyze_php_file as fn
                return fn
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning(f"tree-sitter analyzer for '{language}' not available: {e}")
        return None

    def _node_to_component(self, node, language: str) -> 'CodeComponent':
        """Convert a tree-sitter Node to a CodeComponent."""
        return CodeComponent(
            id=node.id,
            node=None,
            component_type=node.component_type,
            file_path=node.file_path,
            relative_path=node.relative_path,
            source_code=node.source_code,
            start_line=node.start_line,
            end_line=node.end_line,
            has_docstring=node.has_docstring,
            docstring=node.docstring,
            language=language,
            parameters=node.parameters,
            base_classes=node.base_classes,
            class_name=node.class_name,
        )

    def _parse_file_with_treesitter(self, file_path: str, relative_path: str, language: str):
        """Parse a non-Python source file using a tree-sitter based language analyzer."""
        analyzer_fn = self._get_treesitter_analyzer(language)
        if analyzer_fn is None:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return

        try:
            nodes, relationships = analyzer_fn(file_path, content, self.repo_path)
        except Exception as e:
            logger.warning(f"Error running tree-sitter analyzer on {file_path}: {e}")
            return

        # Convert Nodes to CodeComponents
        component_ids_in_file: Dict[str, str] = {}  # node.id -> component.id
        for node in nodes:
            component = self._node_to_component(node, language)
            self.components[component.id] = component
            component_ids_in_file[node.id] = component.id

        # Resolve CallRelationships into depends_on sets
        for rel in relationships:
            caller_id = component_ids_in_file.get(rel.caller, rel.caller)
            callee_id = component_ids_in_file.get(rel.callee, rel.callee)
            if rel.is_resolved and caller_id in self.components and callee_id in self.components:
                self.components[caller_id].depends_on.add(callee_id)
            elif caller_id in self.components:
                # Store unresolved; will be matched after all files are parsed
                self.components[caller_id].depends_on.add(callee_id)

    def _resolve_dependencies(self):
        """
        Second pass to resolve dependencies between components.
        Only processes Python components; non-Python dependencies are resolved
        during tree-sitter parsing.
        """
        for component_id, component in self.components.items():
            # Skip non-Python components — their dependencies are set by tree-sitter analyzers
            if component.language != "python":
                continue
            file_path = component.file_path
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source = f.read()
                
                # Parse file to get imports
                tree = ast.parse(source)
                
                # Add parent field to AST nodes for easier traversal
                add_parent_to_nodes(tree)
                
                # Collect imports
                import_collector = ImportCollector()
                import_collector.visit(tree)
                
                # Find the component node in the tree
                component_node = None
                module_path = self._file_to_module_path(component.relative_path)
                
                if component.component_type == "function":
                    # Find top-level function
                    for node in ast.iter_child_nodes(tree):
                        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) 
                                and node.name == component.id.split(".")[-1]):
                            component_node = node
                            break
                
                elif component.component_type == "class":
                    # Find class
                    for node in ast.iter_child_nodes(tree):
                        if isinstance(node, ast.ClassDef) and node.name == component.id.split(".")[-1]:
                            component_node = node
                            break
                
                elif component.component_type == "method":
                    # Find method inside class
                    class_name, method_name = component.id.split(".")[-2:]
                    class_node = None
                    
                    for node in ast.iter_child_nodes(tree):
                        if isinstance(node, ast.ClassDef) and node.name == class_name:
                            class_node = node
                            for item in node.body:
                                if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) 
                                        and item.name == method_name):
                                    component_node = item
                                    break
                            break
                
                if component_node:
                    # Collect dependencies for this specific component
                    dependency_collector = DependencyCollector(
                        import_collector.imports,
                        import_collector.from_imports,
                        module_path,
                        self.modules
                    )
                    
                    # For functions and methods, collect variables defined in the function
                    if isinstance(component_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Add function parameters to local variables
                        for arg in component_node.args.args:
                            dependency_collector.local_variables.add(arg.arg)
                            
                    dependency_collector.visit(component_node)
                    
                    # Add dependencies to the component
                    component.depends_on.update(dependency_collector.dependencies)
                    
                    # Filter out non-existent dependencies
                    component.depends_on = {
                        dep for dep in component.depends_on 
                        if dep in self.components or dep.split(".", 1)[0] in self.modules
                    }
                
            except (SyntaxError, UnicodeDecodeError) as e:
                logger.warning(f"Error analyzing dependencies in {file_path}: {e}")
    
    def _add_class_method_dependencies(self):
        """
        Third pass to make classes dependent on their methods (except __init__).
        """
        # Group components by class
        class_methods = {}
        
        # Collect all methods for each class
        for component_id, component in self.components.items():
            if component.component_type == "method":
                parts = component_id.split(".")
                if len(parts) >= 2:
                    method_name = parts[-1]
                    class_id = ".".join(parts[:-1])
                    
                    if class_id not in class_methods:
                        class_methods[class_id] = []
                    
                    # Don't include __init__ methods as dependencies of the class
                    if method_name != "__init__":
                        class_methods[class_id].append(component_id)
        
        # Add method dependencies to their classes
        for class_id, method_ids in class_methods.items():
            if class_id in self.components:
                class_component = self.components[class_id]
                for method_id in method_ids:
                    class_component.depends_on.add(method_id)
    
    def _get_source_segment(self, source: str, node: ast.AST) -> str:
        """Get source code segment for an AST node."""
        try:
            if hasattr(ast, "get_source_segment"):
                segment = ast.get_source_segment(source, node)
                if segment is not None:
                    return segment
            
            # Fallback to manual extraction
            lines = source.split("\n")
            start_line = node.lineno - 1
            end_line = getattr(node, "end_lineno", node.lineno) - 1
            return "\n".join(lines[start_line:end_line + 1])
        
        except Exception as e:
            logger.warning(f"Error getting source segment: {e}")
            return ""

    @staticmethod
    def _format_imports(imports: set, from_imports: dict) -> Optional[str]:
        """Render import_collector state as a Python import block string."""
        lines = []
        for name in sorted(imports):
            lines.append(f"import {name}")
        for module in sorted(from_imports):
            names = from_imports[module]
            lines.append(f"from {module} import {', '.join(sorted(names))}" if names else f"from {module} import *")
        return "\n".join(lines) if lines else None


    def _get_docstring(self, source: str, node: ast.AST) -> str:
        """Get the docstring for a given AST node."""
        try:
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                for item in node.body:
                    if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                        if isinstance(item.value.value, str):
                            return item.value.value
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                        if isinstance(item.value.value, str):
                            return item.value.value
            return ""
        except Exception as e:
            logger.warning(f"Error getting docstring: {e}")
            return ""
    
    def save_dependency_graph(self, output_path: str):
        """Save the dependency graph to a JSON file."""
        # Convert to serializable format
        serializable_components = {
            comp_id: component.to_dict()
            for comp_id, component in self.components.items()
        }
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serializable_components, f, indent=2)
        
        logger.info(f"Saved dependency graph to {output_path}")
    
    def load_dependency_graph(self, input_path: str):
        """Load the dependency graph from a JSON file."""
        with open(input_path, "r", encoding="utf-8") as f:
            serialized_components = json.load(f)
        
        # Convert back to CodeComponent objects
        self.components = {
            comp_id: CodeComponent.from_dict(comp_data)
            for comp_id, comp_data in serialized_components.items()
        }
        
        logger.info(f"Loaded {len(self.components)} components from {input_path}")
        return self.components 