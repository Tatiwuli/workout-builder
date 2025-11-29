"""
Benchmark the workout workflow multiple times and report latency statistics.
"""
from __future__ import annotations

import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import numpy as np
import json

from backend.app.agents.build_workout_plan import WorkoutBuilderWorkflow

logger = logging.getLogger("llm_benchmark")


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
_file_lock = threading.Lock()


def run_single_workflow(
    run_id: int,
    output_folder: Path,
    user_input: Dict[str, Any]
) -> None:
    """Run a single workflow and save result immediately to a file."""
    workflow = WorkoutBuilderWorkflow(stream_response=True)
    file_path = output_folder / f"run_{run_id:03d}.json"
    logger.info(f"User input {user_input}")
    try:
        
        final_plan, metadata_records = workflow.run_workflow(processed_responses=user_input)
        total_time = sum(
            record.get("total_time", 0.0) for record in metadata_records if isinstance(record, dict)
        )
        result = {
            "run": run_id,
            "status": "success",
            "user_input": user_input,
            "final_plan": final_plan,
            "metadata_records": metadata_records,
            "total_workflow_time": total_time,
        }
    except Exception as exc:
        result = {
            "run": run_id,
            "status": "error",
            "error": str(exc),
            "user_input": user_input,
            "final_plan": None,
            "metadata_records": [],
            "total_workflow_time": None,
        }
    
    # Save result to file 
    with _file_lock:
       
        try:
            file_path.write_text(json.dumps(result, indent=2, sort_keys=False), encoding="utf-8")
            logger.info(f"Saved run {run_id} to {file_path}")
        except Exception as e:  
            logger.warning(f"Failed to write result for run {run_id} to {file_path}: {e}")


def run_benchmarks(n_iterations: int, output_folder: Path) -> Path:
    """
    Run benchmarks with 2 parallel workflows per iteration.
    
    Args:
        n_iterations: Number of iterations (each runs 2 workflows in parallel = 2*n_iterations total runs)
        output_folder: Folder to save individual run results
        
    Returns:
        Path to the output folder
    """
    output_folder.mkdir(parents=True, exist_ok=True)
    
    run_id = 1
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        
        for iteration in range(1, n_iterations + 1):
            logger.info(f"Starting iteration {iteration}/{n_iterations}")
            
            # Submit 2 workflows in parallel for this iteration
            for _ in range(2):
                logger.info(f"Run id {run_id}\n\n")
                user_input = generate_user_input()
                future = executor.submit(run_single_workflow, run_id, output_folder, user_input)
                futures.append(future)
                run_id += 1
            
            # Wait for both workflows in this iteration to complete
            for future in as_completed(futures[-2:]):
                try:
                    future.result()
                except Exception as e:  
                    logger.error(f"Workflow failed with exception: {e}")
    
    logger.info(f"All {run_id - 1} runs completed. Results saved to {output_folder}")
    return output_folder


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------


def basic_stats(values: List[float]) -> Dict[str, float]:
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



def load_results_from_folder(folder_path: Path) -> List[RunResult]:
    """Load all run results from the output folder."""
    results: List[RunResult] = []
    
    # Get all JSON files in the folder, sorted by run number
    json_files = sorted(folder_path.glob("run_*.json"))
    
    for file_path in json_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            result = json.loads(content)
            results.append(result)
        except Exception as e:  
            logger.warning(f"Failed to load {file_path}: {e}")
    
    return results


def summarise_runs(run_results: List[RunResult]) -> Dict[str, Any]:
    """Compute statistics from metadata only."""
    successful_runs = [r for r in run_results if r.get("status") == "success"]
    
    summary: Dict[str, Any] = {
        "total_runs": len(run_results),
        "successful_runs": len(successful_runs),
        "failed_runs": len(run_results) - len(successful_runs),
        "total_time_stats": {},
        "agent_ttft_stats": {
            "agent_1_selector": {},
            "agent_2_planner": {},
            "agent_3_warmup": {},
        },
    }

    if not successful_runs:
        logger.warning("No successful runs to summarise.")
        return summary

    # Extract total workflow times from metadata
    total_times = [r["total_workflow_time"] for r in successful_runs if r["total_workflow_time"] is not None]
    summary["total_time_stats"] = basic_stats(total_times)

    # Extract time to first token for each agent from metadata
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

    summary["agent_ttft_stats"]["agent_1_selector"] = basic_stats(a1_ttft)
    summary["agent_ttft_stats"]["agent_2_planner"] = basic_stats(a2_ttft)
    summary["agent_ttft_stats"]["agent_3_warmup"] = basic_stats(a3_ttft)

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
        ("Agent 3 (Warmup)", summary["agent_ttft_stats"]["agent_3_warmup"]),
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


def render_per_run_details(run_results: List[RunResult]) -> List[Dict[str, Any]]:
    """Extract metadata from run results for summary."""
    run_details: List[Dict[str, Any]] = []
    for entry in run_results:
        run_id = entry["run"]
        status = entry["status"]
        detail: Dict[str, Any] = {
            "run": run_id,
            "status": status,
            "metadata": entry.get("metadata_records", []),
            "total_workflow_time": entry.get("total_workflow_time"),
            "error": entry.get("error"),
        }
        run_details.append(detail)
    return run_details



def save_summary(
    run_details: List[Dict[str, Any]],
    summary_stats: Dict[str, Any],
    target_path: Path,
) -> Path:
    """Save summary statistics to a JSON file."""
    data = {
        "run_details": run_details,
        "summary_stats": summary_stats,
    }

    summary_file = target_path / "summary.json"
    summary_file.write_text(json.dumps(data, indent=2, sort_keys=False), encoding="utf-8")
    print(f"\nSaved summary statistics to {summary_file}")
    return summary_file

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    n_iterations = 5  # Each iteration runs 2 workflows in parallel = 10 total runs
    
    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir.parent / "data" / "bechmarks"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped folder: Run_MM_DD_HH_MM_SS
    timestamp = datetime.now().strftime("%m_%d_%H_%M_%S")
    output_folder = output_dir / f"Run_{timestamp}"

    print(f"Starting benchmark: {n_iterations} iterations (2 parallel workflows each = {n_iterations * 2} total runs)")
    print(f"Results will be saved to: {output_folder}")
    
    # Run benchmarks (saves results incrementally)
    run_benchmarks(n_iterations, output_folder)
    
    # Load all results from folder
    print("\nLoading results from folder...")
    results = load_results_from_folder(output_folder)
    
    # Compute statistics from metadata
    print("Computing statistics from metadata...")
    summary = summarise_runs(results)
    run_details = render_per_run_details(results)
    
    # Save summary
    save_summary(run_details, summary, output_folder)


if __name__ == "__main__":
    main()