"""Analytics logger for MemDocAgent efficiency metrics."""

import os
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


class AnalyticsLogger:
    """Collects and persists MemDocAgent efficiency metrics as structured JSON."""

    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        self._run_start = time.time()
        self._run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.repo_summary: Dict[str, Any] = {}
        self.dependency_analysis_time: Optional[float] = None

        # per-component start timestamps (removed from JSON output)
        self._start_times: Dict[str, float] = {}

        # per-component action stats: {comp_id: {Read_calls, Write_calls, ...}}
        self._per_component: Dict[str, Dict[str, Any]] = {}

        # agent-level totals
        self._agent_total_calls: Dict[str, int] = {
            "Read": 0, "Write": 0, "Verify": 0, "Finish": 0
        }
        self._agent_total_time: Dict[str, float] = {
            "Read": 0.0, "Write": 0.0, "Verify": 0.0
        }
        # per-action LLM token totals
        self._action_token_totals: Dict[str, Dict[str, int]] = {
            "Read": {"input_tokens": 0, "output_tokens": 0},
            "Write": {"input_tokens": 0, "output_tokens": 0},
            "Verify": {"input_tokens": 0, "output_tokens": 0},
            "Finish": {"input_tokens": 0, "output_tokens": 0},
        }

        # aggregate fetch type totals
        self._total_graph_searches: int = 0
        self._total_memory_hits: int = 0

        # cross-component duplicate tracking:
        # fetched_name → list of focal_component_ids that fetched it
        self._fetched_by: Dict[str, List[str]] = {}

        # per-component LLM token deltas
        self._per_component_llm: Dict[str, Dict[str, Any]] = {}

        # final LLM stats per agent/model
        self._agent_llm_stats: Dict[str, Dict[str, Any]] = {}

        # trajectory: ordered list of task records, each with per-turn steps
        self._trajectories: List[Dict[str, Any]] = []
        self._task_traj_idx: Dict[str, int] = {}  # target -> index in _trajectories

    # ------------------------------------------------------------------
    # Static / one-shot logging
    # ------------------------------------------------------------------

    def log_repo_summary(
        self,
        file_count: int,
        function_count: int,
        class_count: int,
        method_count: int,
        topological_order: List[str],
        module_count: int = 0,
        repo_count: int = 1,
    ) -> None:
        self.repo_summary = {
            "file_count": file_count,
            "function_count": function_count,
            "class_count": class_count,
            "method_count": method_count,
            "total_components": function_count + class_count + method_count,
            "module_count": module_count,
            "repo_count": repo_count,
            "topological_order_count": len(topological_order),
            "topological_order": list(topological_order),
        }

    def log_dependency_analysis_time(self, elapsed: float) -> None:
        self.dependency_analysis_time = elapsed

    # ------------------------------------------------------------------
    # Per-component tracking
    # ------------------------------------------------------------------

    def start_component(self, component_id: str) -> None:
        self._start_times[component_id] = time.time()
        self._per_component[component_id] = {
            "Read_calls": 0,
            "Write_calls": 0,
            "Verify_calls": 0,
            "Finish_calls": 0,
            "Read_time": 0.0,
            "Write_time": 0.0,
            "Verify_time": 0.0,
            "total_time_seconds": None,
            "graph_searches": 0,
            "memory_hits": 0,
        }

    def end_component(
        self,
        component_id: str,
        llm_deltas: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Mark a component as done: record elapsed time and LLM token deltas."""
        start = self._start_times.get(component_id)
        elapsed = round(time.time() - start, 3) if start is not None else None
        if component_id in self._per_component:
            self._per_component[component_id]["total_time_seconds"] = elapsed
        if llm_deltas:
            self._per_component_llm[component_id] = llm_deltas

    def log_agent_call(
        self,
        component_id: str,
        action_name: str,
        elapsed: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> None:
        """Record one action call (Read/Write/Verify/Finish) for a component.

        Args:
            component_id: Component being processed.
            action_name: One of Read, Write, Verify, Finish.
            elapsed: Wall-clock seconds for this action.
            input_tokens: LLM input tokens consumed by this action call.
            output_tokens: LLM output tokens consumed by this action call.
        """
        if component_id not in self._per_component:
            self.start_component(component_id)

        calls_key = f"{action_name}_calls"
        time_key = f"{action_name}_time"

        self._per_component[component_id][calls_key] = (
            self._per_component[component_id].get(calls_key, 0) + 1
        )
        if time_key in self._per_component[component_id]:
            self._per_component[component_id][time_key] = (
                self._per_component[component_id].get(time_key, 0.0) + elapsed
            )

        if action_name in self._agent_total_calls:
            self._agent_total_calls[action_name] += 1
        if action_name in self._agent_total_time:
            self._agent_total_time[action_name] += elapsed

        # Track per-action token usage
        if action_name in self._action_token_totals:
            self._action_token_totals[action_name]["input_tokens"] += input_tokens
            self._action_token_totals[action_name]["output_tokens"] += output_tokens

    def log_read_access(
        self,
        component_id: str,
        graph_count: int,
        memory_count: int,
        fetched_names: Optional[List[str]] = None,
    ) -> None:
        """Record graph-search and memory-hit counts for one Read action.

        Args:
            component_id: Focal component being processed.
            graph_count: Number of dependency-graph source lookups.
            memory_count: Number of RepoMemory cache hits.
            fetched_names: Component IDs that were accessed (for cross-component
                duplicate tracking).
        """
        if component_id in self._per_component:
            self._per_component[component_id]["graph_searches"] += graph_count
            self._per_component[component_id]["memory_hits"] += memory_count
        self._total_graph_searches += graph_count
        self._total_memory_hits += memory_count

        if fetched_names:
            for name in fetched_names:
                if name not in self._fetched_by:
                    self._fetched_by[name] = []
                if component_id not in self._fetched_by[name]:
                    self._fetched_by[name].append(component_id)

    # ------------------------------------------------------------------
    # Verify score tracking
    # ------------------------------------------------------------------

    def log_verify_scores(
        self,
        component_id: str,
        attempt: int,
        scores: Optional[Dict[str, float]],
        weighted_avg: Optional[float],
        conflict_score: Optional[float],
        final_score: float,
        passed: bool,
    ) -> None:
        """Record detailed verify scores for one verify attempt.

        Each component accumulates a list of verify attempts so that score
        progression across revisions is preserved.

        Args:
            component_id: The component being verified.
            attempt: 1-based verify attempt number (1 = first, 2 = after revision).
            scores: Per-criterion scores {CONSISTENCY, COMPLETENESS, HELPFULNESS}.
            weighted_avg: Weighted average of the 3 criterion scores.
            conflict_score: Dependency conflict score (1.0 = no conflict).
            final_score: Combined score used for pass/fail decision.
            passed: Whether this attempt passed the threshold.
        """
        if not hasattr(self, "_verify_scores"):
            self._verify_scores: Dict[str, List[Dict[str, Any]]] = {}

        if component_id not in self._verify_scores:
            self._verify_scores[component_id] = []

        entry: Dict[str, Any] = {
            "attempt": attempt,
            "passed": passed,
            "final_score": round(final_score, 4),
        }
        if scores is not None:
            entry["CONSISTENCY"] = round(scores.get("CONSISTENCY", 0.0), 4)
            entry["COMPLETENESS"] = round(scores.get("COMPLETENESS", 0.0), 4)
            entry["HELPFULNESS"] = round(scores.get("HELPFULNESS", 0.0), 4)
        if weighted_avg is not None:
            entry["weighted_avg"] = round(weighted_avg, 4)
        if conflict_score is not None:
            entry["conflict_score"] = round(conflict_score, 4)

        self._verify_scores[component_id].append(entry)

    # ------------------------------------------------------------------
    # LLM stats
    # ------------------------------------------------------------------

    def log_final_llm_stats(
        self,
        agent_name: str,
        requests: int,
        in_tok: int,
        out_tok: int,
        cost: float,
    ) -> None:
        self._agent_llm_stats[agent_name] = {
            "total_requests": requests,
            "total_input_tokens": in_tok,
            "total_output_tokens": out_tok,
            "total_cost_usd": cost,
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _compute_cross_component_duplicates(self) -> Dict[str, Any]:
        """Compute which fetched components were accessed by 2+ focal components."""
        duplicate_map: Dict[str, List[str]] = {
            name: focal_list
            for name, focal_list in self._fetched_by.items()
            if len(focal_list) >= 2
        }
        return {
            "duplicate_component_count": len(duplicate_map),
            "total_fetched_component_types": len(self._fetched_by),
            "redundant_fetch_count": sum(
                len(v) - 1 for v in duplicate_map.values()
            ),
            "duplicates": {
                name: {"accessed_by": focal_list, "access_count": len(focal_list)}
                for name, focal_list in sorted(
                    duplicate_map.items(), key=lambda x: -len(x[1])
                )
            },
        }

    # ------------------------------------------------------------------
    # Trajectory logging
    # ------------------------------------------------------------------

    def start_task_trajectory(self, task_type: str, target: str, file_path: str = "") -> None:
        """Begin a new trajectory record for a task."""
        entry: Dict[str, Any] = {
            "task_type": task_type,
            "target": target,
            "file_path": file_path,
            "turns": [],
        }
        self._task_traj_idx[target] = len(self._trajectories)
        self._trajectories.append(entry)

    def log_trajectory_turn(
        self,
        target: str,
        turn: int,
        thought: str,
        action: str,
        action_input: str,
        observation: str,
    ) -> None:
        """Append one Thought/Action/Observation step to a task's trajectory."""
        idx = self._task_traj_idx.get(target)
        if idx is None:
            return
        self._trajectories[idx]["turns"].append({
            "turn": turn,
            "thought": thought,
            "action": action,
            "action_input": action_input,
            "observation": observation,
        })

    def save_trajectory(self, label: str = "run") -> str:
        """Persist the full trajectory to ``trajectory.json`` in the log directory.

        Returns:
            Absolute path to the written file.
        """
        data = {
            "run_id": self._run_id,
            "label": label,
            "trajectories": self._trajectories,
        }
        out_path = os.path.join(self.log_dir, "trajectory.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return out_path

    # ------------------------------------------------------------------
    # NLI Conflict stats
    # ------------------------------------------------------------------

    def log_conflict_stats(
        self,
        component_id: str,
        total_candidate_pairs: int,
        entailment_count: int,
        contradiction_count: int,
        neutral_count: int,
        conflict_score: float,
        dep_ids_checked: List[str],
    ) -> None:
        """Record NLI-based conflict detection results for one component."""
        if not hasattr(self, "_conflict_stats"):
            self._conflict_stats: Dict[str, Dict[str, Any]] = {}
        self._conflict_stats[component_id] = {
            "total_candidate_pairs": total_candidate_pairs,
            "entailment_count": entailment_count,
            "contradiction_count": contradiction_count,
            "neutral_count": neutral_count,
            "conflict_score": round(conflict_score, 4),
            "dep_ids_checked": dep_ids_checked,
        }

    # ------------------------------------------------------------------
    # Summary computations (called by save())
    # ------------------------------------------------------------------

    def _compute_efficiency_summary(self) -> Dict[str, Any]:
        n_comp = len(self._per_component) or 1
        total_calls = sum(self._agent_total_calls.values())
        total_fetches = self._total_memory_hits + self._total_graph_searches
        hit_rate = self._total_memory_hits / total_fetches if total_fetches > 0 else 0.0

        total_tokens = 0
        total_cost = 0.0
        for v in self._per_component_llm.values():
            total_tokens += v.get("input_tokens", 0) + v.get("output_tokens", 0)
            total_cost += v.get("cost", 0.0)
        if total_cost == 0.0:
            for v in self._agent_llm_stats.values():
                total_cost += v.get("total_cost_usd", 0.0)
        if total_tokens == 0:
            for v in self._agent_llm_stats.values():
                total_tokens += v.get("total_input_tokens", 0) + v.get("total_output_tokens", 0)

        total_time = sum(
            s.get("total_time_seconds", 0) or 0 for s in self._per_component.values()
        )
        return {
            "avg_time_per_component_seconds": round(total_time / n_comp, 3),
            "avg_turns_per_component": round(total_calls / n_comp, 2),
            "memory_hit_rate": round(hit_rate, 4),
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(total_cost, 4),
            "avg_tokens_per_component": round(total_tokens / n_comp, 1),
        }

    def _compute_per_level_stats(self) -> Dict[str, Dict[str, Any]]:
        from collections import Counter
        levels: Dict[str, Dict[str, Any]] = {}
        for traj in self._trajectories:
            tt = traj.get("task_type", "UNKNOWN")
            if tt not in levels:
                levels[tt] = {
                    "count": 0,
                    "total_time_seconds": 0.0,
                    "total_turns": 0,
                    "action_counts": Counter(),
                }
            entry = levels[tt]
            entry["count"] += 1
            target = traj.get("target", "")
            comp_stats = self._per_component.get(target, {})
            entry["total_time_seconds"] += comp_stats.get("total_time_seconds", 0) or 0
            turns = traj.get("turns", [])
            entry["total_turns"] += len(turns)
            for turn in turns:
                action = turn.get("action", "Unknown")
                entry["action_counts"][action] += 1

        result: Dict[str, Dict[str, Any]] = {}
        for tt, entry in levels.items():
            n = entry["count"] or 1
            result[tt] = {
                "count": entry["count"],
                "total_time_seconds": round(entry["total_time_seconds"], 3),
                "avg_time_seconds": round(entry["total_time_seconds"] / n, 3),
                "total_turns": entry["total_turns"],
                "avg_turns": round(entry["total_turns"] / n, 2),
                "action_counts": dict(entry["action_counts"]),
            }
        return result

    def _compute_verify_summary(self) -> Dict[str, Any]:
        vs = getattr(self, "_verify_scores", {})
        if not vs:
            return {}

        total_attempts = 0
        first_pass_success = 0
        required_revision = 0
        score_parse_failures = 0
        first_scores: Dict[str, List[float]] = {"CONSISTENCY": [], "COMPLETENESS": [], "HELPFULNESS": []}
        improvements: Dict[str, List[float]] = {"CONSISTENCY": [], "COMPLETENESS": [], "HELPFULNESS": []}

        for comp_id, attempts in vs.items():
            for a in attempts:
                total_attempts += 1
                if a.get("CONSISTENCY") is None:
                    score_parse_failures += 1
                if a["attempt"] == 1 and a["passed"]:
                    first_pass_success += 1
            if len(attempts) >= 2:
                required_revision += 1

            # First attempt scores
            if attempts and attempts[0].get("CONSISTENCY") is not None:
                for k in first_scores:
                    first_scores[k].append(attempts[0].get(k, 0.0))

            # Improvement: last attempt - first attempt
            if len(attempts) >= 2:
                first = attempts[0]
                last = attempts[-1]
                if first.get("CONSISTENCY") is not None and last.get("CONSISTENCY") is not None:
                    for k in improvements:
                        improvements[k].append(last.get(k, 0.0) - first.get(k, 0.0))

        avg_first = {k: round(sum(v) / len(v), 4) if v else 0.0 for k, v in first_scores.items()}
        avg_improve = {k: round(sum(v) / len(v), 4) if v else 0.0 for k, v in improvements.items()}

        return {
            "total_verify_attempts": total_attempts,
            "first_pass_success": first_pass_success,
            "required_revision": required_revision,
            "score_parse_failures": score_parse_failures,
            "avg_first_attempt_scores": avg_first,
            "avg_score_improvement": avg_improve,
        }

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, label: str = "run") -> str:
        total_run_time = time.time() - self._run_start

        data = {
            "run_id": self._run_id,
            "label": label,
            "total_run_time_seconds": round(total_run_time, 3),
            "repo_summary": self.repo_summary,
            "dependency_analysis_time_seconds": (
                round(self.dependency_analysis_time, 3)
                if self.dependency_analysis_time is not None
                else None
            ),
            "action_call_totals": dict(self._agent_total_calls),
            "action_time_totals_seconds": {
                k: round(v, 3) for k, v in self._agent_total_time.items()
            },
            "action_token_totals": dict(self._action_token_totals),
            "read_fetch_totals": {
                "total_graph_searches": self._total_graph_searches,
                "total_memory_hits": self._total_memory_hits,
            },
            "per_component_stats": self._per_component,
            "per_component_verify_scores": getattr(self, "_verify_scores", {}),
            "per_component_llm_stats": self._per_component_llm,
            "cross_component_duplicate_fetches": self._compute_cross_component_duplicates(),
            "agent_llm_stats": self._agent_llm_stats,
            "efficiency_summary": self._compute_efficiency_summary(),
            "per_level_stats": self._compute_per_level_stats(),
            "per_component_conflict_stats": getattr(self, "_conflict_stats", {}),
            "verify_summary": self._compute_verify_summary(),
        }

        out_path = os.path.join(self.log_dir, f"analytics_{label}.json")

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return out_path
