# Copyright (c) Meta Platforms, Inc. and affiliates
"""
Topological sorting utilities for dependency graphs with cycle handling.

This module provides functions to perform topological sorting on a dependency graph,
including detection and resolution of dependency cycles.
"""

import logging
import os
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

def detect_cycles(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """
    Detect cycles in a dependency graph using Tarjan's algorithm to find
    strongly connected components.
    
    Args:
        graph: A dependency graph represented as adjacency lists
               (node -> set of dependencies)
    
    Returns:
        A list of lists, where each inner list contains the nodes in a cycle
    """
    # Implementation of Tarjan's algorithm
    index_counter = [0]
    index = {}  # node -> index
    lowlink = {}  # node -> lowlink value
    onstack = set()  # nodes currently on the stack
    stack = []  # stack of nodes
    result = []  # list of cycles (strongly connected components)
    
    def strongconnect(node):
        # Set the depth index for node
        index[node] = index_counter[0]
        lowlink[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        onstack.add(node)
        
        # Consider successors
        for successor in graph.get(node, set()):
            if successor not in index:
                # Successor has not yet been visited; recurse on it
                strongconnect(successor)
                lowlink[node] = min(lowlink[node], lowlink[successor])
            elif successor in onstack:
                # Successor is on the stack and hence in the current SCC
                lowlink[node] = min(lowlink[node], index[successor])
        
        # If node is a root node, pop the stack and generate an SCC
        if lowlink[node] == index[node]:
            # Start a new strongly connected component
            scc = []
            while True:
                successor = stack.pop()
                onstack.remove(successor)
                scc.append(successor)
                if successor == node:
                    break
            
            # Only include SCCs with more than one node (actual cycles)
            if len(scc) > 1:
                result.append(scc)
    
    # Visit each node
    for node in graph:
        if node not in index:
            strongconnect(node)
    
    return result

def resolve_cycles(graph: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    Resolve cycles in a dependency graph by identifying strongly connected
    components and breaking cycles.
    
    Args:
        graph: A dependency graph represented as adjacency lists
               (node -> set of dependencies)
    
    Returns:
        A new acyclic graph with the same nodes but with cycles broken
    """
    # Detect cycles (SCCs)
    cycles = detect_cycles(graph)
    
    if not cycles:
        logger.info("No cycles detected in the dependency graph")
        return graph
    
    logger.info(f"Detected {len(cycles)} cycles in the dependency graph")
    
    # Create a copy of the graph to modify
    new_graph = {node: deps.copy() for node, deps in graph.items()}
    
    # Process each cycle
    for i, cycle in enumerate(cycles):
        logger.info(f"Cycle {i+1}: {' -> '.join(cycle)}")
        
        # Strategy: Break the cycle by removing the "weakest" dependency
        # Here, we just arbitrarily remove the last edge to make the graph acyclic
        # In a real-world scenario, you might use heuristics to determine which edge to break
        # For example, removing edges between different modules before edges within the same module
        for j in range(len(cycle) - 1):
            current = cycle[j]
            next_node = cycle[j + 1]
            
            if next_node in new_graph[current]:
                logger.info(f"Breaking cycle by removing dependency: {current} -> {next_node}")
                new_graph[current].remove(next_node)
                break
    
    return new_graph

def topological_sort(graph: Dict[str, Set[str]]) -> List[str]:
    """
    Perform a topological sort on a dependency graph.
    
    Args:
        graph: A dependency graph represented as adjacency lists
               (node -> set of dependencies)
    
    Returns:
        A list of nodes in topological order (dependencies first)
    """
    # First, check for and resolve cycles
    acyclic_graph = resolve_cycles(graph)
    
    # Initialize in-degree counter for all nodes
    in_degree = {node: 0 for node in acyclic_graph}
    
    # Count in-degrees
    for node, dependencies in acyclic_graph.items():
        for dep in dependencies:
            if dep in in_degree:
                in_degree[dep] += 1
    
    # Queue of nodes with no dependencies (in-degree of 0)
    queue = deque([node for node, degree in in_degree.items() if degree == 0])
    
    # Result list to store the topological order
    result = []
    
    # Process nodes in topological order
    while queue:
        node = queue.popleft()
        result.append(node)
        
        # Reduce in-degree for each node that depends on the current node
        for dependent, deps in acyclic_graph.items():
            if node in deps:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
    
    # Check if the sort was successful (all nodes included)
    if len(result) != len(acyclic_graph):
        logger.warning("Topological sort failed: graph has cycles that weren't resolved")
        # Return all nodes in some order to avoid breaking the process
        return list(acyclic_graph.keys())
    
    # Reverse the result to get dependencies first
    return result[::-1]

def dependency_first_dfs(graph: Dict[str, Set[str]]) -> List[str]:
    """
    Topological ordering via iterative post-order DFS.

    Edge semantics: A → B means "A depends on B" (B must be processed before A).

    For a unified graph produced by build_graph_from_components(repo_id=...) the
    returned list has the form:

        [leaf_components…, inner_components…,
         leaf_modules…,    parent_modules…,
         repo_id]

    i.e. every dependency appears strictly before the node that requires it.

    Cycles are broken by resolve_cycles() before traversal, so the graph is
    guaranteed to be a DAG when DFS runs.

    Args:
        graph: dependency graph {node: set_of_dependencies}

    Returns:
        list of node IDs in dependency-first (topological) order
    """
    acyclic = resolve_cycles(graph)

    # Root nodes = nodes with no incoming edge (nothing depends on them).
    # In a unified graph with a repo node, the repo is typically the sole root.
    has_incoming: Dict[str, bool] = {n: False for n in acyclic}
    for node, deps in acyclic.items():
        for dep in deps:
            if dep in has_incoming:
                has_incoming[dep] = True

    roots = sorted(n for n in acyclic if not has_incoming[n])
    if not roots:
        logger.warning("No root nodes found; using first node as starting point")
        roots = [sorted(acyclic.keys())[0]]

    visited: Set[str] = set()
    result: List[str] = []

    def visit(start: str) -> None:
        # Iterative post-order DFS with a two-phase marker.
        # (node, is_post=True) → emit node after all its deps have been emitted.
        stack: List[Tuple[str, bool]] = [(start, False)]

        while stack:
            node, is_post = stack.pop()

            if is_post:
                # All dependencies have been processed; emit this node now.
                if node not in visited:
                    visited.add(node)
                    result.append(node)
                continue

            if node in visited:
                continue

            # Push the "emit" marker first so it fires after all deps are done.
            stack.append((node, True))

            # Push unvisited deps in reverse-sorted order so the first
            # alphabetically is processed first (deterministic output).
            for dep in sorted(acyclic.get(node, set()), reverse=True):
                if dep not in visited:
                    stack.append((dep, False))

    for root in roots:
        visit(root)

    # Pick up any isolated nodes not reachable from the identified roots.
    for node in sorted(acyclic.keys()):
        if node not in visited:
            visit(node)

    return result


def build_graph_from_components(
    components: Dict[str, Any],
    repo_id: Optional[str] = None,
) -> Dict[str, Set[str]]:
    """
    Build a unified dependency graph covering three hierarchy levels.

    Edge semantics: A → B means "A depends on B" (B must come before A).

    Levels added to the graph
    -------------------------
    1. **Component layer** (always built):
       comp_id → {dep_comp_ids}
       A component depends on the other components it uses in code.

    2. **Module layer** (when repo_id is not None):
       module_path → {direct_component_ids ∪ child_module_paths}
       A module must wait for all its contents to be processed first.

    3. **Repo layer** (when repo_id is not None):
       repo_id → {root_module_paths ∪ top_level_component_ids}
       The repo summary is the very last item to be produced.

    Running dependency_first_dfs on the returned graph gives a flat list:

        [components in dep order …, leaf modules …, parent modules …, repo_id]

    Args:
        components: mapping {comp_id: CodeComponent} from DependencyParser
        repo_id:    unique identifier for the repo node (e.g. repo directory name).
                    Pass None to get a component-only graph (backward-compatible).

    Returns:
        Unified dependency graph ready for dependency_first_dfs.
    """
    graph: Dict[str, Set[str]] = {}

    # ── Level 1: component → code-dependency edges ────────────────────────
    for comp_id, component in components.items():
        graph.setdefault(comp_id, set())
        for dep_id in component.depends_on:
            if dep_id in components:
                graph[comp_id].add(dep_id)

    if repo_id is None:
        return graph

    # ── Build module hierarchy from component file paths ──────────────────
    # module_direct_comps[dir] = set of comp IDs whose file lives directly in dir
    module_direct_comps: Dict[str, Set[str]] = defaultdict(set)
    # module_children_map[parent] = set of immediate child module paths
    module_children_map: Dict[str, Set[str]] = defaultdict(set)
    all_modules: Set[str] = set()
    top_level_comps: Set[str] = set()   # components with no parent directory

    for comp_id, comp in components.items():
        rel_path: str = getattr(comp, 'relative_path', None) or ''
        directory = os.path.dirname(rel_path) if rel_path else ''
        if not directory:
            top_level_comps.add(comp_id)
            continue

        module_direct_comps[directory].add(comp_id)
        all_modules.add(directory)

        # Walk up the directory tree, registering parent→child links.
        current = directory
        while True:
            parent = os.path.dirname(current)
            if not parent or parent == current:
                break
            module_children_map[parent].add(current)
            all_modules.add(parent)
            current = parent

    # ── Level 2: module → {direct_components + child_modules} edges ───────
    for mod in all_modules:
        graph[mod] = (
            module_direct_comps.get(mod, set())
            | module_children_map.get(mod, set())
        )

    # ── Level 3: repo → {root_modules + top_level_components} edges ───────
    # Root modules = modules whose parent directory is not itself a module.
    root_modules: Set[str] = {
        m for m in all_modules
        if os.path.dirname(m) not in all_modules
    }
    if all_modules:
        graph[repo_id] = root_modules | top_level_comps
    else:
        # No modules at all — repo directly depends on every component.
        graph[repo_id] = set(components.keys())

    return graph