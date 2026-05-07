#!/usr/bin/env python3
"""Resume MODULE + REPO-level documentation for a repository.

Loads existing documentation.json, marks all components as done,
then re-runs only the specified missing modules and the repo-level task.

Usage:
    python resume_module_repo.py \
        --repo-path /path/to/source/repo \
        --output-dir ./output \
        --config-path config/agent_config.yaml \
        --mode without_think2 \
        --modules hypertools/plot
"""
import argparse
import json
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.manager_agent import ManagerAgent
from src.memory.repo_memory import RepoMemory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_memory_from_json(doc_path: str) -> RepoMemory:
    """Rebuild RepoMemory from an existing documentation.json."""
    with open(doc_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    memory = RepoMemory()

    for comp_id, comp in data.get("components", {}).items():
        memory.set_component_summary(
            component_id=comp_id,
            file_path=comp.get("file_path", ""),
            confidence=comp.get("confidence") or 0.0,
            documentation=comp.get("documentation", ""),
            claims=comp.get("claims") or [],
            component_type=comp.get("component_type"),
        )

    for mod_path, mod in data.get("modules", {}).items():
        memory.set_module_summary(
            module_path=mod_path,
            documentation=mod.get("documentation", ""),
            component_ids=mod.get("component_ids") or [],
            claims=mod.get("claims") or [],
        )

    logger.info(
        "Loaded memory: %d components, %d modules",
        len(memory.list_component_ids()),
        len(memory.list_module_paths()),
    )
    return memory


def main():
    parser = argparse.ArgumentParser(description="Resume MODULE + REPO-level documentation")
    parser.add_argument("--repo-path", required=True, help="Path to source repository")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--config-path", default="config/agent_config.yaml")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument(
        "--mode", default="default",
        choices=["default", "only_self", "without_memory", "without_think", "without_think2", "ver2"],
        help="Ablation mode (must match the original run)",
    )
    parser.add_argument(
        "--modules", nargs="+", default=[],
        help="Module paths to re-generate (e.g. hypertools/plot). "
             "If empty, all modules with empty documentation are re-run.",
    )
    args = parser.parse_args()

    logging.getLogger().setLevel(getattr(logging, args.log_level))

    repo_path = os.path.abspath(args.repo_path)
    repo_name = os.path.basename(repo_path)
    output_dir = os.path.abspath(args.output_dir)
    doc_path = os.path.join(output_dir, "documentation", repo_name, "documentation.json")

    if not os.path.isfile(doc_path):
        logger.error("documentation.json not found: %s", doc_path)
        sys.exit(1)

    # Resolve ablation flags
    ablation_mode = args.mode
    skip_conflict = ablation_mode == "only_self"
    without_memory = ablation_mode == "without_memory"
    without_think = ablation_mode in ("without_think", "without_think2")
    without_think2 = ablation_mode == "without_think2"
    ver2_mode = ablation_mode == "ver2"

    # 1. Load existing memory
    memory = load_memory_from_json(doc_path)

    # 2. Create ManagerAgent with matching mode flags
    manager = ManagerAgent(
        repo_path=repo_path,
        config_path=args.config_path,
        output_dir=output_dir,
        skip_conflict_check=skip_conflict,
        without_memory=without_memory,
        without_think=without_think,
        without_think2=without_think2,
        ver2_mode=ver2_mode,
    )

    # 3. Replace memory
    manager.memory = memory
    manager.worker.repo_memory = memory

    # 4. Mark all components as done
    for comp_id in manager.topo_order:
        manager.component_status[comp_id] = "done"

    # 5. Mark all existing modules as done
    for mod_path in manager.module_status:
        if memory.has_module_summary(mod_path):
            mod_entry = memory.get_module_summary(mod_path)
            if mod_entry and mod_entry.documentation and mod_entry.documentation.strip():
                manager.module_status[mod_path] = "done"

    # 6. Determine which modules to re-run
    if args.modules:
        target_modules = args.modules
    else:
        target_modules = [
            mp for mp, status in manager.module_status.items()
            if status != "done"
        ]

    logger.info("=== Resuming MODULE + REPO tasks for %s (mode=%s) ===", repo_name, ablation_mode)
    logger.info("Target modules: %s", target_modules)
    t0 = time.perf_counter()

    # 7. Run missing module tasks
    for mod_path in target_modules:
        logger.info("Running MODULE task: %s", mod_path)
        manager.module_status[mod_path] = "pending"
        manager._run_module_task(mod_path)
        logger.info("  → %s: %s", mod_path, manager.module_status.get(mod_path))

    # 8. Run REPO task
    logger.info("Running REPO task...")
    manager._run_repo_task()

    elapsed = time.perf_counter() - t0
    logger.info("Completed in %.1f s", elapsed)

    # 9. Save updated documentation.json
    repo_entry = memory.get_repo_summary(repo_name)
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

    if repo_entry and repo_entry.documentation:
        logger.info("Repo doc preview: %s...", repo_entry.documentation[:200])
    else:
        logger.warning("Repo documentation is still empty!")


if __name__ == "__main__":
    main()
