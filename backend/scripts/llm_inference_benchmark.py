"""
Benchmark the workout workflow multiple times and report latency statistics.
"""
from __future__ import annotations

import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


import numpy as np
import json

from backend.app.agents.build_workout_plan import WorkoutBuilderWorkflow  
from backend.app.utils.agent_utils import save_output_to_json

LOGGER = logging.getLogger("llm_benchmark")


# ---------------------------------------------------------------------------
# Synthetic input generation helpers
# ---------------------------------------------------------------------------

MUSCLE_GOAL_OPTIONS: Dict[str, List[str]] = {
    "back": ["Wider Back", "Thicker Back", "Defined Back"],
    "chest": ["Upper Chest Focus", "Lower Chest Focus", "Overall Chest Growth"],
    "shoulders": ["3D Shoulders", "Strong Shoulders", "Defined Shoulders"],
    "triceps": ["Bigger Triceps", "Defined Triceps", "Pressing Power"],
    "glutes": ["Lifted Glutes", "Fuller Glutes", "Glute Strength"],
    "hamstrings": ["Bigger Hamstrings", "Defined Hamstrings", "Explosive Power"],
    "quadriceps": ["Bigger Quads", "Defined Quads", "Leg Power"],
    "calves": ["Bigger Calves", "Defined Calves", "Functional Strength"],
}

FREQUENCY_OPTIONS = [2, 3, 4]

EXPERIENCE_LEVELS: Dict[str, str] = {
    "beginners": "I'm just starting out and have less than 3 months of experience.",
    "intermediate_early": "I've been training regularly for 1 to 2 years.",
    "intermediate_late": "I've been training regularly for 2 to 3 years.",
}


def generate_user_input() -> Dict[str, Any]:
    muscles = random.sample(
        ["Back", "Chest", "Shoulders", "Triceps", "Glutes", "Hamstrings", "Quadriceps", "Calves"],
        k=4,
    )

    goals: Dict[str, List[str]] = {}
    muscle_workout_frequency: Dict[str, int] = {}

    for muscle in muscles:
        slug = muscle.lower().replace(" ", "_")
        options = MUSCLE_GOAL_OPTIONS[slug]
        n_goals = random.randint(1, len(options))
        goals[f"{slug}_goal"] = random.sample(options, n_goals)
        muscle_workout_frequency[f"{slug}_frequency"] = random.choice(FREQUENCY_OPTIONS)

    workout_duration = random.choice([30, 45, 60, 75, 90])
    if workout_duration < 45:
        time_constraint = "short"
    elif workout_duration <= 60:
        time_constraint = "medium"
    else:
        time_constraint = "long"

    fitness_level = random.choice(list(EXPERIENCE_LEVELS.keys()))
    experience_level_description = EXPERIENCE_LEVELS[fitness_level]

    return {
        "muscle_groups": [m.lower() for m in muscles],
        "goals": goals,
        "muscle_workout_frequency": muscle_workout_frequency,
        "workout_duration": workout_duration,
        "time_constraint": time_constraint, 
        "fitness_level": fitness_level, 
        "experience_level_description": experience_level_description,
    }


# ---------------------------------------------------------------------------
# Benchmark execution
# ---------------------------------------------------------------------------

RunResult = Dict[str, Any]


def _write_partial_results(partial_path: Path, run_results: List[RunResult]) -> None:
    payload = {"runs": run_results}
    try:
        partial_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Failed to write partial results to %s: %s", partial_path, exc)


def run_benchmarks(n_runs: int, partial_path: Optional[Path] = None) -> List[RunResult]:
    workflow = WorkoutBuilderWorkflow(stream_response=True)
    results: List[RunResult] = []

    for run_idx in range(1, n_runs + 1):
        user_input = generate_user_input()
        try:
            final_plan, metadata_records = workflow.run_workflow(processed_responses=user_input)
            total_time = sum(
                record.get("total_time", 0.0) for record in metadata_records if isinstance(record, dict)
            )
            results.append(
                {
                    "run": run_idx,
                    "status": "success",
                    "user_input": user_input,
                    "final_plan": final_plan,
                    "metadata_records": metadata_records,
                    "total_workflow_time": total_time,
                }
            )
        except Exception as exc:  
            results.append(
                {
                    "run": run_idx,
                    "status": "error",
                    "error": str(exc),
                    "user_input": user_input,
                    "final_plan": None,
                    "metadata_records": [],
                    "total_workflow_time": None,
                }
            )

        if partial_path is not None:
            _write_partial_results(partial_path, results)

    return results


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------


def _basic_stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {}
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p90": float(np.percentile(values, 90)),
        "p95": float(np.percentile(values, 95)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }



def summarise_runs(run_results: List[RunResult]) -> Dict[str, Any]:
    successful_runs = [r for r in run_results if r.get("status") == "success"]
    
    summary: Dict[str, Any] = {
        "total_runs": len(run_results),
        "successful_runs": len(successful_runs),
        "failed_runs": len(run_results) - len(successful_runs),
        "total_time_stats": {},
        "agent_ttft_stats": {
            "agent_1_selector": {},
            "agent_2_planner": {},
            "agent_3_trainer": {},
        },
    }

    if not successful_runs:
        LOGGER.warning("No successful runs to summarise.")
        return summary

    total_times = [r["total_workflow_time"] for r in successful_runs if r["total_workflow_time"] is not None]
    #compute the metrics for total time
    summary["total_time_stats"] = _basic_stats(total_times)

    #compute time first token for every agent
    a1_ttft = [
        (r["metadata_records"][0].get("time_first_token", 0.0) if r["metadata_records"] else 0.0)
        for r in successful_runs
    ]
    a2_ttft = [
        (r["metadata_records"][1].get("time_first_token", 0.0) if len(r["metadata_records"]) > 1 else 0.0)
        for r in successful_runs
    ]
    a3_ttft = [
        (r["metadata_records"][2].get("time_first_token", 0.0) if len(r["metadata_records"]) > 2 else 0.0)
        for r in successful_runs
    ]

    summary["agent_ttft_stats"]["agent_1_selector"] = _basic_stats(a1_ttft)
    summary["agent_ttft_stats"]["agent_2_planner"] = _basic_stats(a2_ttft)
    summary["agent_ttft_stats"]["agent_3_trainer"] = _basic_stats(a3_ttft)

    # --- Console output ---
    print("\n--- Summary Statistics (for successful runs) ---")
    print(
        f"Total runs: {summary['total_runs']}, successful: {summary['successful_runs']}, "
        f"failed: {summary['failed_runs']}"
    )

    if summary["total_time_stats"]:
        stats = summary["total_time_stats"]
        print("\nTotal Workflow Time (s):")
        print(f"  Mean:   {stats['mean']:.2f}")
        print(f"  Median: {stats['median']:.2f} (p50)")
        print(f"  p90:    {stats['p90']:.2f}")
        print(f"  p95:    {stats['p95']:.2f}")
        print(f"  Min:    {stats['min']:.2f}")
        print(f"  Max:    {stats['max']:.2f}")
    
    for label, stats in (
        ("Agent 3 (Trainer)", summary["agent_ttft_stats"]["agent_3_trainer"]),
        ("Agent 2 (Planner)", summary["agent_ttft_stats"]["agent_2_planner"]),
        ("Agent 1 (Selector)", summary["agent_ttft_stats"]["agent_1_selector"]),
    ):
        print(f"\n{label} TTFT stats:")
        if not stats:
            print("  no data")
        else:
            for key, value in stats.items():
                print(f"  {key}: {value:.2f}")

    return summary


def render_per_run_details(run_results: List[RunResult]) -> None:
    print("\n--- Detailed Run Results ---")
    run_details: List[Dict[str, Any]] = []
    for entry in run_results:
        run_id = entry["run"]
        status = entry["status"]
        detail: Dict[str, Any] = {
            "run": run_id,
            "status": status,
            "user_input": entry["user_input"],
            "final_plan": entry["final_plan"],
            "metadata": entry["metadata_records"],
            "total_workflow_time": entry.get("total_workflow_time"),
            "error": entry.get("error"),
        }
        run_details.append(detail)

        print(f"\nRun #{run_id} — status: {status}")
        print("=" * 60)
        if status != "success":
            print(f"Error: {entry.get('error')}")
            continue

        print("User input:")
        print(json.dumps(entry["user_input"], indent=2, sort_keys=True))

        print("\nFinal plan:")
        print(json.dumps(entry["final_plan"], indent=2, sort_keys=True))

        print("\nMetadata:")
        for record in entry["metadata_records"]:
            print(json.dumps(record, indent=2, sort_keys=True))

        print("-" * 60)

    return run_details



def save_results(
    run_details: List[Dict[str, Any]],
    summary_stats: Dict[str, Any],
    target_path: Optional[Path] = None,
) -> Path:
    data = {
        "run_details": run_details,
        "summary_stats": summary_stats,
    }

    if target_path is not None:
        target_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        print(f"\nSaved benchmark results to {target_path}")
        return target_path

    saved_path = Path(
        save_output_to_json(data, "benchmark_results")
    )
    print(f"\nSaved benchmark results to {saved_path}")
    return saved_path

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    runs = 10
    output_dir = Path("backend/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"llm_benchmark_{timestamp}.json"

    results = run_benchmarks(runs, partial_path=output_path)
    summary = summarise_runs(results)
    run_details = render_per_run_details(results)
    save_results(run_details, summary, target_path=output_path)


if __name__ == "__main__":
    main()