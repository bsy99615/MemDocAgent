"""Manager Agent — orchestrates repository-level documentation.

Coordinates the full documentation pipeline:
  1. Parse repository and build dependency graph.
  2. Dispatch COMPONENT tasks to WorkerAgent in topological order
     (dependencies first).
  3. When all components in a module are done, dispatch a MODULE task.
  4. When all modules are done, dispatch a REPO task.

State
-----
component_status : Dict[component_id, "pending"|"done"]
module_status    : Dict[module_path,   "pending"|"done"]
repo_status      : "pending"|"done"
"""
from __future__ import annotations

import logging
import os
import time
from typing import Dict, List, Optional, Set
from print_color import print

try:
    from ..dependency_analyzer.ast_parser import DependencyParser
    from ..dependency_analyzer.topo_sort import dependency_first_dfs, build_graph_from_components
    from ..memory.repo_memory import RepoMemory
    from .worker_agent import WorkerAgent, WorkerTask, TaskType
    from ..analytics_logger import AnalyticsLogger
except ImportError:
    from dependency_analyzer.ast_parser import DependencyParser
    from dependency_analyzer.topo_sort import dependency_first_dfs, build_graph_from_components
    from memory.repo_memory import RepoMemory
    from agent.worker_agent import WorkerAgent, WorkerTask, TaskType
    from analytics_logger import AnalyticsLogger

logger = logging.getLogger(__name__)

_STATUS_PENDING = "pending"
_STATUS_DONE    = "done"


class ManagerAgent:
    """Orchestrates repository-level documentation via WorkerAgent.

    Usage::

        manager = ManagerAgent(repo_path="path/to/repo", config_path="config/agent_config.yaml")
        manager.run()

    After ``run()`` completes, ``manager.memory`` holds all generated
    documentation accessible via :meth:`RepoMemory.get_component_summary`
    and :meth:`RepoMemory.get_module_summary`.
    """

    def __init__(
        self,
        repo_path: str,
        config_path: Optional[str] = None,
        skip_conflict_check: bool = False,
        without_memory: bool = False,
        without_think: bool = False,
        without_think2: bool = False,
        ver2_mode: bool = False,
        output_dir: Optional[str] = None,
    ) -> None:
        self.repo_path   = os.path.abspath(repo_path)
        self.config_path = config_path
        self.skip_conflict_check = skip_conflict_check
        self.without_memory = without_memory
        self.without_think = without_think
        self.without_think2 = without_think2
        self.ver2_mode = ver2_mode
        self.output_dir = output_dir

        # ── 1. Parse repository ───────────────────────────────────────
        logger.info("Parsing repository: %s", self.repo_path)
        parser = DependencyParser(self.repo_path)
        self.components = parser.parse_repository()   # Dict[str, CodeComponent]
        self.dep_graph  = parser.dependency_graph     # Dict[str, List[str]]
        
        
        """
        self.components: Dict[str, CodeComponent]
            Key: component_id (e.g. "src.agent.reader.read_file")
            Value: CodeComponent with metadata
                - id
                - node
                - component_type (function, method, class,,,)
                - file_path
                - relative_path
                - depends_on
                - source_code
                - start_line
                - end_line
                - has_docstring
                - docstring
        """
        
        # logger.info(self.components)
        # print("===================")
        # print(self.dep_graph, color="yellow")

        # ── 2. Topological order (component → module → repo) ─────────────
        # Build a unified dependency graph that includes three layers:
        #   component → component (code dependencies)
        #   module    → {direct_components + child_modules}
        #   repo      → {root_modules + top_level_components}
        # dependency_first_dfs then returns a single flat list where every
        # dependency appears before the node that requires it, giving the
        # natural processing order:
        #   [leaf_comps…, inner_comps…, leaf_modules…, parent_modules…, repo]
        self._repo_id: str = os.path.basename(self.repo_path)
        graph_sets = build_graph_from_components(
            self.components, repo_id=self._repo_id
        )
        self.topo_order: List[str] = dependency_first_dfs(graph_sets)

        # ── 3. Status tracking ────────────────────────────────────────
        # Partition topo_order into three disjoint sets.
        self.component_status: Dict[str, str] = {
            tid: _STATUS_PENDING
            for tid in self.topo_order
            if tid in self.components
        }

        all_module_paths: Set[str] = {
            tid for tid in self.topo_order
            if tid not in self.components and tid != self._repo_id
        }
        self.module_status: Dict[str, str] = {
            m: _STATUS_PENDING for m in all_module_paths
        }
        self.repo_status: str = _STATUS_PENDING

        # module_children[mod] = immediate child module paths
        # (deps of mod that are themselves modules, not components)
        self.module_children: Dict[str, Set[str]] = {
            mid: {
                dep for dep in graph_sets.get(mid, set())
                if dep not in self.components
            }
            for mid in all_module_paths
        }

        # Root modules / top-level components are the direct deps of the repo node.
        _repo_deps: Set[str] = graph_sets.get(self._repo_id, set())
        self.root_module_paths: List[str] = sorted(
            dep for dep in _repo_deps if dep not in self.components
        )
        # Preserve topo order for root components (deps of repo that are comps).
        self.root_component_ids: List[str] = [
            tid for tid in self.topo_order
            if tid in self.components and tid in _repo_deps
        ]

        n_comps = len(self.component_status)
        n_mods  = len(all_module_paths)
        logger.info(
            "Topo order: %d components, %d modules, repo=%s",
            n_comps, n_mods, self._repo_id,
        )
        logger.info(
            "Module hierarchy: %d total modules, %d root modules, %d top-level components",
            n_mods, len(self.root_module_paths), len(self.root_component_ids),
        )

        # ── 4. Shared memory + Analytics ──────────────────────────────
        self.memory = RepoMemory()
        repo_name = os.path.basename(self.repo_path) # e.g. "vending_machine" for "path/to/vending_machine"
        if self.output_dir:
            analytics_dir = os.path.join(self.output_dir, "analytics", repo_name)
        else:
            analytics_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "..", "output", "analytics", repo_name,
            )
        self.analytics = AnalyticsLogger(log_dir=os.path.normpath(analytics_dir))

        # Log repo summary
        n_func = sum(1 for c in self.components.values() if c.component_type == "function")
        n_cls  = sum(1 for c in self.components.values() if c.component_type == "class")
        n_meth = sum(1 for c in self.components.values() if c.component_type == "method")
        n_file = len({c.file_path for c in self.components.values() if c.file_path})
        n_mod = len(all_module_paths)
        comp_topo_order = [t for t in self.topo_order if t in self.components]
        self.analytics.log_repo_summary(
            n_file, n_func, n_cls, n_meth, comp_topo_order,
            module_count=n_mod, repo_count=1,
        )

        # ── 5. WorkerAgent ────────────────────────────────────────────
        self.worker = WorkerAgent(
            repo_path=self.repo_path,
            repo_memory=self.memory,
            dep_graph=self.dep_graph,
            components=self.components,
            config_path=self.config_path,
            analytics=self.analytics,
            skip_conflict_check=self.skip_conflict_check,
            without_memory=self.without_memory,
            without_think=self.without_think,
            without_think2=self.without_think2,
            ver2_mode=self.ver2_mode,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> RepoMemory:
        """Run the full documentation pipeline and return the memory store.

        Returns:
            :class:`RepoMemory` containing all generated documentation.
        """
        logger.info("=== ManagerAgent: starting documentation run ===")

        _dep_t0 = time.perf_counter()
        self.analytics.log_dependency_analysis_time(time.perf_counter() - _dep_t0)

        # Single pass over the pre-computed topo_order.
        # The order already guarantees:
        #   component deps → component → all components in module → module
        #   → all child modules of parent → parent module → repo
        for task_id in self.topo_order:
            if task_id in self.components:
                self._run_component_task(task_id)
            elif task_id == self._repo_id:
                self._run_repo_task()
            else:
                self._run_module_task(task_id)

        # ── LLM stats snapshot ────────────────────────────────────────
        llm = getattr(self.worker, "llm", None)
        rl  = getattr(llm, "rate_limiter", None)
        if rl is not None:
            self.analytics.log_final_llm_stats(
                agent_name="WorkerAgent",
                requests=rl.total_requests,
                in_tok=rl.total_input_tokens,
                out_tok=rl.total_output_tokens,
                cost=rl.total_cost,
            )

        logger.info("=== ManagerAgent: documentation run complete ===")
        return self.memory

    # ------------------------------------------------------------------
    # Task runners
    # ------------------------------------------------------------------

    def _run_component_task(self, comp_id: str) -> None:
        """Dispatch a COMPONENT WorkerTask and mark it done."""
        comp = self.components[comp_id]

        logger.info("Running component task for '%s' (file: %s)", comp_id, comp.relative_path)

        # WorkerAgent에게 COMPONENT task 전달
        task = WorkerTask(
            type=TaskType.COMPONENT,
            target=comp_id,
            file_path=comp.relative_path,
            source_code=comp.source_code,
            imports=comp.imports,
        )
        logger.info("[COMPONENT] %s (%s)", comp_id, comp.relative_path)
        try:
            # WorkerAgent가 COMPONENT task를 처리하는 동안, ManagerAgent는 해당 컴포넌트의 상태를 "pending"으로 유지.
            self.worker.process(task)
        except Exception as exc:
            logger.error("WorkerAgent failed on component '%s': %s", comp_id, exc)
        finally:
            # WorkerAgent가 COMPONENT task 처리를 완료하면, ManagerAgent는 해당 컴포넌트의 상태를 "done"으로 업데이트.
            self.component_status[comp_id] = _STATUS_DONE

    def _run_module_task(self, module_path: str) -> None:
        """Dispatch a MODULE WorkerTask and mark it done."""
        direct_cids = self._components_directly_in(module_path)
        direct_files = sorted({
            self.components[cid].relative_path
            for cid in direct_cids
            if cid in self.components and self.components[cid].relative_path
        })
        child_mps = sorted(self.module_children.get(module_path, set()))
        task = WorkerTask(
            type=TaskType.MODULE,
            target=module_path,
            file_path=module_path,
            file_paths=direct_files,
            component_ids=direct_cids,
            child_module_paths=child_mps,
        )
        logger.info(
            "[MODULE] %s (direct_components=%d, child_modules=%d)",
            module_path, len(direct_cids), len(child_mps),
        )
        try:
            self.worker.process(task)
        except Exception as exc:
            logger.error("WorkerAgent failed on module '%s': %s", module_path, exc)
        finally:
            self.module_status[module_path] = _STATUS_DONE

    def _run_repo_task(self) -> None:
        """Dispatch the single REPO WorkerTask."""
        task = WorkerTask(
            type=TaskType.REPO,
            target=os.path.basename(self.repo_path),
            file_path=self.repo_path,
            module_paths=self.root_module_paths,
            component_ids=self.root_component_ids,
        )
        logger.info("[REPO] %s", self.repo_path)
        try:
            self.worker.process(task)
        except Exception as exc:
            logger.error("WorkerAgent failed on repo task: %s", exc)
        finally:
            self.repo_status = _STATUS_DONE

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _components_directly_in(self, dir_path: str) -> List[str]:
        """Return component IDs whose source file is directly in *dir_path*."""
        return [
            cid for cid in self.topo_order
            if cid in self.components
            and os.path.dirname(
                self.components[cid].relative_path or ""
            ) == dir_path
        ]

    # ------------------------------------------------------------------
    # Progress reporting
    # ------------------------------------------------------------------

    def progress(self) -> Dict[str, object]:
        """Return a snapshot of the current pipeline progress."""
        n_total = len(self.component_status)
        n_done  = sum(1 for s in self.component_status.values() if s == _STATUS_DONE)
        m_total = len(self.module_status)
        m_done  = sum(1 for s in self.module_status.values() if s == _STATUS_DONE)
        return {
            "components": {"done": n_done, "total": n_total},
            "modules":    {"done": m_done, "total": m_total},
            "repo":       self.repo_status,
        }

    def __repr__(self) -> str:
        p = self.progress()
        return (
            f"ManagerAgent("
            f"repo={self.repo_path!r}, "
            f"components={p['components']['done']}/{p['components']['total']}, "
            f"modules={p['modules']['done']}/{p['modules']['total']}, "
            f"repo={p['repo']})"
        )
