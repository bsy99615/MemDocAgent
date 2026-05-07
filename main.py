#!/usr/bin/env python3
"""MemDocAgent — Repository-Level Documentation Framework

Entry point for the Manager/Worker agent pipeline.

Usage
-----
    python main.py --repo-path <PATH> [--config-path <PATH>] [--log-level <LEVEL>]

Examples
--------
    # Document a local repository with default config
    python main.py --repo-path ./my_project

    # Use a custom config (e.g. different LLM or thresholds)
    python main.py --repo-path ./my_project --config-path config/agent_config.yaml

    # Verbose logging for debugging
    python main.py --repo-path ./my_project --log-level DEBUG
"""

import argparse
import logging
import os
import sys
import time

import colorlog

# Make src/ importable when running from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent.manager_agent import ManagerAgent
from agent.worker_agent import MarkdownExporter


def _setup_logging(level: str) -> None:                                                                                                            
      numeric_level = getattr(logging, level.upper(), logging.INFO)                                                                                  
                                                                                                                                                     
      # ── 기본 root handler ─────────────────────────────────────────────                                                                           
      root_handler = logging.StreamHandler(sys.stdout)                                                                                               
      root_handler.setFormatter(colorlog.ColoredFormatter(                                                                                           
          "%(asctime)s  %(log_color)s%(levelname)-8s%(reset)s  %(name)s — %(message)s"                                                               
      ))                                                                                                                                             
      logging.basicConfig(level=numeric_level, handlers=[root_handler])                                                                              
                                                                                                                                                     
      # ── Manager → 노란색 ──────────────────────────────────────────────                                                                           
      _add_colored_handler(                                                                                                                          
          logger_name="agent.manager_agent",                                                                                                         
          level=numeric_level,                              
          color="yellow",                                                                                                                            
      )                                                                                                                                              
                                                                                                                                                     
      # ── Worker → 초록색 ───────────────────────────────────────────────                                                                           
      _add_colored_handler(                                 
          logger_name="agent.worker_agent",
          level=numeric_level,                                                                                                                       
          color="green",                                                                                                                             
      )                                                                                                                                              
                                                                                                                                                     
                                                    
def _add_colored_handler(logger_name: str, level: int, color: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(colorlog.ColoredFormatter(                                                                                                
        "%(asctime)s  %(log_color)s%(levelname)-8s%(reset)s  %(name)s — %(message)s",
        log_colors={k: color for k in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")},                                                          
    ))                                                                                                                                             
    lg = logging.getLogger(logger_name)                                                                                                            
    lg.addHandler(handler)                                                                                                                         
    lg.propagate = False  # root handler 중복 출력 방지
      

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MemDocAgent: automated repository-level documentation via Manager/Worker agents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo-path",
        required=True,
        help="Path to the Python repository to document.",
    )
    parser.add_argument(
        "--config-path",
        default="config/agent_config.yaml",
        help="Path to the agent configuration YAML (default: config/agent_config.yaml).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO).",
    )
    parser.add_argument(
        "--no-conflict-check",
        action="store_true",
        default=False,
        help="Disable cross-dependency conflict check during verification.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Root directory for all outputs (documentation, analytics, trajectory). "
             "Defaults to <project_root>/output.",
    )
    parser.add_argument(
        "--mode",
        default="default",
        choices=["default", "only_self", "without_memory", "without_think", "without_think2", "ver2"],
        help="Ablation mode: "
             "'default' = full pipeline, "
             "'only_self' = verify with self-consistency only (no conflict check), "
             "'without_memory' = no RepoMemory retrieval (always read from source), "
             "'without_think' = partial: Thought parsing skipped but still generated, "
             "'without_think2' = full: NOTHINK prompt + Thought stripped from memory, "
             "'ver2' = filtered memory (essential sections only) + simple code passthrough.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _setup_logging(args.log_level)
    logger = logging.getLogger("main")

    repo_path = os.path.abspath(args.repo_path)
    if not os.path.isdir(repo_path):
        logger.error("repo-path does not exist or is not a directory: %s", repo_path)
        sys.exit(1)

    config_path = args.config_path
    if not os.path.isfile(config_path):
        logger.error("config-path not found: %s", config_path)
        sys.exit(1)

    logger.info("Repository : %s", repo_path)
    logger.info("Config     : %s", config_path)

    # ── Run pipeline ───────────────────────────────────────────────────
    t0 = time.perf_counter()

    output_dir = os.path.abspath(args.output_dir) if args.output_dir else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "output",
    )

    # Resolve ablation flags from --mode
    ablation_mode = args.mode
    skip_conflict = args.no_conflict_check or ablation_mode == "only_self"
    without_memory = ablation_mode == "without_memory"
    without_think = ablation_mode == "without_think"
    without_think2 = ablation_mode == "without_think2"
    ver2_mode = ablation_mode == "ver2"

    logger.info("Mode       : %s", ablation_mode)

    manager = ManagerAgent(
        repo_path=repo_path,
        config_path=config_path,
        skip_conflict_check=skip_conflict,
        without_memory=without_memory,
        without_think=without_think or without_think2,
        without_think2=without_think2,
        ver2_mode=ver2_mode,
        output_dir=output_dir,
    )
    logger.info("Initialised — %r", manager)

    memory = manager.run()

    elapsed = time.perf_counter() - t0

    # ── Summary ────────────────────────────────────────────────────────
    progress = manager.progress()
    components_done = progress["components"]["done"]
    components_total = progress["components"]["total"]
    modules_done = progress["modules"]["done"]
    modules_total = progress["modules"]["total"]

    logger.info("─" * 60)
    logger.info("Documentation complete in %.1f s", elapsed)
    logger.info(
        "  Components : %d / %d documented",
        components_done, components_total,
    )
    logger.info(
        "  Modules    : %d / %d summarised",
        modules_done, modules_total,
    )
    logger.info(
        "  Repo       : %s",
        "✓" if manager.repo_status == "done" else "✗",
    )
    logger.info("  Memory     : %r", memory)
    logger.info("─" * 60)

    # ── Save documentation to JSON ─────────────────────────────────────
    repo_name = os.path.basename(repo_path)
    doc_dir = os.path.join(output_dir, "documentation", repo_name)
    os.makedirs(doc_dir, exist_ok=True)
    doc_path = os.path.join(doc_dir, "documentation.json")

    import json
    repo_entry = memory.get_repo_summary(repo_name)
    # Build depends_on lookup from parsed components
    depends_on_map = {
        cid: list(comp.depends_on) for cid, comp in manager.components.items()
    }

    doc_data = {
        "repo_path": repo_path,
        "elapsed_seconds": round(elapsed, 3),
        "components": {
            cid: {
                "file_path": entry.file_path,
                "component_type": entry.component_type,
                "confidence": entry.confidence,
                "documentation": entry.documentation,
                "claims": entry.claims,
                "depends_on": depends_on_map.get(cid, []),
            }
            for cid, entry in memory.get_all_component_summaries().items()
        },
        "modules": {
            path: {
                "module_path": entry.module_path,
                "component_ids": entry.component_ids,
                "documentation": entry.documentation,
                "claims": entry.claims,
            }
            for path, entry in memory.get_all_module_summaries().items()
        },
        "repository": {
            "documentation": repo_entry.documentation if repo_entry else None,
            "module_paths": repo_entry.module_paths if repo_entry else [],
            "claims": repo_entry.claims if repo_entry else [],
        },
    }

    with open(doc_path, "w", encoding="utf-8") as f:
        json.dump(doc_data, f, indent=2, ensure_ascii=False)

    logger.info("Documentation saved → %s", doc_path)

    # ── Save dependency graph ─────────────────────────────────────────
    dep_graph_dir = os.path.join(output_dir, "dependency_graphs", repo_name)
    os.makedirs(dep_graph_dir, exist_ok=True)
    dep_graph_path = os.path.join(dep_graph_dir, f"{repo_name}_dependency_graph.json")
    dep_graph_data = {
        cid: comp.to_dict() for cid, comp in manager.components.items()
    }
    with open(dep_graph_path, "w", encoding="utf-8") as f:
        json.dump(dep_graph_data, f, indent=2, ensure_ascii=False)
    logger.info("Dependency graph saved → %s", dep_graph_path)

    # ── Export markdown documentation tree ────────────────────────────
    exporter = MarkdownExporter(
        repo_memory=memory,
        repo_name=repo_name,
        output_dir=doc_dir,
        components=manager.components,
    )
    root_md = exporter.export()
    logger.info("Markdown docs saved  → %s", root_md)

    # ── Save analytics ─────────────────────────────────────────────────
    analytics_path = manager.analytics.save(label=repo_name)
    logger.info("Analytics saved     → %s", analytics_path)

    trajectory_path = manager.analytics.save_trajectory(label=repo_name)
    logger.info("Trajectory saved    → %s", trajectory_path)


if __name__ == "__main__":
    main()
