#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates
"""
Tool to remove docstrings from Python files in a repository.
"""

import os
import ast
import astor
import argparse
from typing import List, Tuple


class DocstringRemover(ast.NodeTransformer):
    """
    AST NodeTransformer that removes docstrings from classes, methods, and functions.
    """
    
    def visit_ClassDef(self, node):
        """Remove docstrings from class definitions."""
        # Process class body first (recursive)
        node = self.generic_visit(node)
        
        # Remove docstring if present
        if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Str)):
            node.body = node.body[1:]
        
        return node
    
    def visit_FunctionDef(self, node):
        """Remove docstrings from function/method definitions."""
        # Process function body first (recursive)
        node = self.generic_visit(node)
        
        # Remove docstring if present
        if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Str)):
            node.body = node.body[1:]
        
        return node
    
    def visit_AsyncFunctionDef(self, node):
        """Remove docstrings from async function/method definitions."""
        # Process function body first (recursive)
        node = self.generic_visit(node)
        
        # Remove docstring if present
        if (node.body and isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Str)):
            node.body = node.body[1:]
        
        return node


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the given directory and its subdirectories."""
    python_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files


def remove_docstrings_from_file(file_path: str, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Remove docstrings from a Python file.
    
    Args:
        file_path: Path to the Python file
        dry_run: If True, don't actually write changes to file
        
    Returns:
        Tuple of (success, message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the source code into an AST
        tree = ast.parse(source)
        
        # Remove docstrings
        transformer = DocstringRemover()
        new_tree = transformer.visit(tree)
        
        # Generate the modified source code
        new_source = astor.to_source(new_tree)
        
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_source)
            
            return True, f"Successfully removed docstrings from {file_path}"
        else:
            return True, f"Would remove docstrings from {file_path} (dry run)"
    
    except Exception as e:
        return False, f"Error processing {file_path}: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Remove docstrings from Python files in a repository")
    parser.add_argument("directory", help="Directory containing Python files to process")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually modify files, just show what would be done")
    args = parser.parse_args()
    
    # Find all Python files
    python_files = find_python_files(args.directory)
    print(f"Found {len(python_files)} Python files to process")
    
    # Process each file
    success_count = 0
    for file_path in python_files:
        success, message = remove_docstrings_from_file(file_path, args.dry_run)
        print(message)
        if success:
            success_count += 1
    
    # Summary
    print(f"\nProcessed {len(python_files)} files, {success_count} successful")


if __name__ == "__main__":
    main() 