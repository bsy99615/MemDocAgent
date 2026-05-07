"""Memory system for the documentation agent framework.

Stores
------
1. component_store  — per-component entry (summary, source, confidence)
2. search_cache     — cached external search results
3. module_store     — per-module aggregate summary
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ComponentEntry:
    """Memory entry for a single code component.

    Attributes:
        summary: Human-readable summary of the component.
        file_path: Absolute or repo-relative path to the source file,
                   e.g. ``"src/agent/reader.py"``.
        source_with_docstring: Full source code including the generated docstring.
        confidence: Confidence score (0.0–1.0) reported by the Verify action.
    """
    id: str = ""  # e.g. "src/agent/reader.Reader.process"
    node: Optional[object] = None  # AST node or similar (optional, for future use)
    component_type: Optional[str] = None  # e.g. "class", "function
    file_path: str = ""
    relative_path: Optional[str] = None  # e.g. "src/agent/reader.py"
    source_code: Optional[str] = None  # raw source code without docstring
    documentation: Optional[str] = None  # generated docstring
    confidence: float = 0.0
    claims: List[str] = field(default_factory=list)


@dataclass
class RepoEntry:
    """Memory entry for the top-level repository summary.

    Attributes:
        documentation: Generated documentation for the entire repository.
        repo_path: Identifier for the repository (e.g. repo name or root path).
        module_paths: Paths of all modules that belong to this repository.
        claims: Atomic factual claims extracted from the documentation.
    """
    documentation: str = ""
    repo_path: str = ""
    module_paths: List[str] = field(default_factory=list)
    claims: List[str] = field(default_factory=list)


@dataclass
class ModuleEntry:
    """Memory entry for a module (directory).

    Attributes:
        documentation: Generated documentation for this module.
        module_path: Repo-relative path to the module directory,
                     e.g. ``"src/agent"`` or ``"django/contrib/gis/db"``.
        component_ids: IDs of components **directly** in this module directory.
        child_module_paths: Paths of direct child modules (sub-directories).
        claims: Atomic factual claims extracted from the documentation.
    """
    documentation: str = ""
    module_path: str = ""
    component_ids: List[str] = field(default_factory=list)
    child_module_paths: List[str] = field(default_factory=list)
    claims: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Claims are stored directly in ComponentEntry.claims (List[str]).
# Conflict detection is handled in WorkerExecutor._evaluate_claim_conflicts.


# ---------------------------------------------------------------------------
# RepoMemory
# ---------------------------------------------------------------------------

class RepoMemory:
    """Shared memory for documentation agents.

    Three stores
    ------------
    component_store : Dict[component_id, ComponentEntry]
        Per-component documentation and confidence score.
        Written by WorkerAgent Finish action; read by subsequent workers via
        the Read action to gather dependency context.

    search_cache : Dict[query, str]
        Cached external search results keyed by query string.
        Prevents redundant API calls across the pipeline.

    module_store : Dict[module_path, ModuleEntry]
        Aggregate module-level summaries, written after all components in a
        module are done (MODULE task) and read during REPO task.

    Usage::

        memory = RepoMemory()

        # Worker stores result after Finish action
        memory.set_component_summary(
            component_id="src/agent/reader.Reader",
            confidence=0.91,
            documentation="class Reader:\\n    ...",
        )

        # Later worker reads dependency context
        entry = memory.get_component_summary("src/agent/reader.Reader")
        print(entry.confidence)  # 0.91
    """

    def __init__(self) -> None:
        self._component_store: Dict[str, ComponentEntry] = {}
        self._search_cache: Dict[str, str] = {}
        self._module_store: Dict[str, ModuleEntry] = {}
        self._repo_store: Dict[str, str] = {}  # repo-level summary store (optional, for future use)

        # TODO: consistency_graph 미구현 (claims 기반 conflict detection용)
        # self._consistency_graph: Dict[str, List[Claim]] = {}

    # ------------------------------------------------------------------
    # component_store
    # ------------------------------------------------------------------

    def get_component_summary(
        self, component_id: str
    ) -> Optional[ComponentEntry]:
        """Look up a component's memory entry.

        Args:
            component_id: Fully-qualified component identifier, e.g.
                ``"src/agent/reader.Reader.process"``.

        Returns:
            :class:`ComponentEntry` if found, otherwise ``None``.
        """
        return self._component_store.get(component_id)

    def set_component_summary(
        self,
        component_id: str,
        file_path: str = "",
        confidence: float = 0.0,
        documentation: str = "",
        source_code: Optional[str] = None,
        claims: Optional[List[str]] = None,
        component_type: Optional[str] = None,
    ) -> None:
        """Store (or overwrite) a component's memory entry.

        Args:
            component_id: Fully-qualified component identifier.
            file_path: Repo-relative path to the source file,
                       e.g. ``"src/agent/reader.py"``.
            confidence: Confidence score from the Verify action (0.0–1.0).
            documentation: Generated documentation for the component (optional).
            source_code: Raw source code of the component. Stored as a fallback
                         when documentation is not yet available so subsequent
                         Read actions can serve source from memory instead of
                         re-fetching from the graph.
            claims: Atomic factual claims extracted from the final documentation.
                    Used as ground-truth in subsequent components' conflict checks.
            component_type: Type of the component (e.g. "function", "class", "method").
        """
        self._component_store[component_id] = ComponentEntry(
            file_path=file_path,
            documentation=documentation,
            confidence=confidence,
            source_code=source_code,
            claims=list(claims) if claims else [],
            component_type=component_type,
        )
        logger.debug(
            "set_component_summary: %s (file=%s, confidence=%.2f)",
            component_id, file_path, confidence,
        )

    def has_component_summary(self, component_id: str) -> bool:
        """Return True if a memory entry exists for *component_id*."""
        return component_id in self._component_store

    def list_component_ids(self) -> List[str]:
        """Return all stored component IDs."""
        return list(self._component_store.keys())

    def get_all_component_summaries(self) -> Dict[str, ComponentEntry]:
        """Return a shallow copy of all component entries."""
        return dict(self._component_store)

    # ------------------------------------------------------------------
    # search_cache
    # ------------------------------------------------------------------

    def get_external_knowledge(self, query: str) -> Optional[str]:
        """Return cached search result for *query*, or ``None``."""
        return self._search_cache.get(query)

    def set_external_knowledge(self, query: str, knowledge: str) -> None:
        """Cache external search result for *query*.

        Args:
            query: The search query string.
            knowledge: The retrieved knowledge text.
        """
        self._search_cache[query] = knowledge
        logger.debug(
            "set_external_knowledge: query=%r (%d chars)", query, len(knowledge)
        )

    def has_external_knowledge(self, query: str) -> bool:
        """Return True if a cached result exists for *query*."""
        return query in self._search_cache

    # ------------------------------------------------------------------
    # module_store
    # ------------------------------------------------------------------

    def get_module_summary(
        self, module_path: str
    ) -> Optional[ModuleEntry]:
        """Look up a module's memory entry.

        Args:
            module_path: Module path, e.g. ``"src/agent"`` or
                         ``"src/agent/reader.py"``.

        Returns:
            :class:`ModuleEntry` if found, otherwise ``None``.
        """
        return self._module_store.get(module_path)

    def set_module_summary(
        self,
        module_path: str,
        documentation: str = "",
        component_ids: Optional[List[str]] = None,
        child_module_paths: Optional[List[str]] = None,
        claims: Optional[List[str]] = None,
    ) -> None:
        """Store (or overwrite) a module's memory entry.

        Args:
            module_path: Repo-relative path to the module directory,
                         e.g. ``"src/agent"``. Also used as the key.
            documentation: Generated documentation for the module.
            component_ids: IDs of components directly in this module directory.
            child_module_paths: Paths of direct child modules (sub-directories).
            claims: Atomic factual claims extracted from the documentation.
        """
        component_ids = component_ids or []
        child_module_paths = child_module_paths or []
        claims = claims or []
        self._module_store[module_path] = ModuleEntry(
            documentation=documentation,
            module_path=module_path,
            component_ids=list(component_ids),
            child_module_paths=list(child_module_paths),
            claims=list(claims),
        )
        logger.debug(
            "set_module_summary: %s (%d components, %d children, %d claims)",
            module_path, len(component_ids), len(child_module_paths), len(claims),
        )

    def has_module_summary(self, module_path: str) -> bool:
        """Return True if a memory entry exists for *module_path*."""
        return module_path in self._module_store

    def list_module_paths(self) -> List[str]:
        """Return all stored module paths."""
        return list(self._module_store.keys())

    def get_all_module_summaries(self) -> Dict[str, ModuleEntry]:
        """Return a shallow copy of all module entries."""
        return dict(self._module_store)

    # ------------------------------------------------------------------
    # repo_store
    # ------------------------------------------------------------------

    def get_repo_summary(self, repo_path: str) -> Optional[RepoEntry]:
        """Look up the repository-level memory entry.

        Args:
            repo_path: Repository identifier used as the store key.

        Returns:
            :class:`RepoEntry` if found, otherwise ``None``.
        """
        return self._repo_store.get(repo_path)

    def set_repo_summary(
        self,
        repo_path: str,
        documentation: str = "",
        module_paths: Optional[List[str]] = None,
        claims: Optional[List[str]] = None,
    ) -> None:
        """Store (or overwrite) the repository-level memory entry.

        Args:
            repo_path: Repository identifier (e.g. repo name or root path).
            documentation: Generated top-level documentation for the repository.
            module_paths: Paths of all modules belonging to this repository.
            claims: Atomic factual claims extracted from the documentation.
        """
        module_paths = module_paths or []
        claims = claims or []
        self._repo_store[repo_path] = RepoEntry(
            documentation=documentation,
            repo_path=repo_path,
            module_paths=list(module_paths),
            claims=list(claims),
        )
        logger.debug(
            "set_repo_summary: %s (%d modules, %d claims)",
            repo_path, len(module_paths), len(claims),
        )

    def has_repo_summary(self, repo_path: str) -> bool:
        """Return True if a memory entry exists for *repo_path*."""
        return repo_path in self._repo_store

    def list_repo_paths(self) -> List[str]:
        """Return all stored repository paths."""
        return list(self._repo_store.keys())

    # ------------------------------------------------------------------
    # TODO: Consistency check — 미구현 (claims 기반)
    # ------------------------------------------------------------------
    # def check_consistency(
    #     self, new_claims: List[str], related_component_ids: List[str]
    # ) -> List[ConsistencyConflict]: ...
    #
    # def get_dependency_claims(
    #     self, component_ids: List[str]
    # ) -> Dict[str, List[Claim]]: ...
    #
    # def record_contradiction(
    #     self, component_id_a: str, component_id_b: str
    # ) -> None: ...

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def clear_all(self) -> None:
        """Clear all stores."""
        self._component_store.clear()
        self._search_cache.clear()
        self._module_store.clear()
        self._repo_store.clear()
        logger.debug("All memory stores cleared.")

    def __repr__(self) -> str:
        return (
            f"RepoMemory("
            f"components={len(self._component_store)}, "
            f"search_cache={len(self._search_cache)}, "
            f"modules={len(self._module_store)}, "
            f"repos={len(self._repo_store)})"
        )
