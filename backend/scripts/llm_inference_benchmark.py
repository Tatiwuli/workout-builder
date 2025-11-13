


"""
Benchmark the streaming workflow multiple times and report latency statistics.
"""

from __future__ import annotations

import copy
import json
import logging
import math
import statistics
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Sequence

from backend.app.agents.build_workout_plan import WorkoutBuilderWorkflow  

import random 
LOGGER = logging.getLogger("llm_benchmark")


#Randomly select 4  muscle groups
def generate_user_input():
    muscle_goals = {
        "back": [
            "Build a broader, V-shaped upper body.",
            "Add depth and strength for a more powerful look.",
            "Sculpt visible lines and muscle tone for a leaner back."
        ],
        "chest": [
            "Lift and fill out the upper chest area.",
            "Add fullness and shape to the lower chest.",
            "Build size and balance across the chest."
        ],
        "shoulders": [
            "Create a rounded, well-defined shoulder shape.",
            "Build stable, powerful shoulders for pressing and lifting.",
            "Emphasize muscle tone and shape for a lean look."
        ],
        "triceps": [
            "Increase muscle size for fuller, stronger arms.",
            "Sharpen the back of your arms for a toned appearance.",
            "Improve strength in push and press movements."
        ],
        "glutes": [
            "Shape and lift your glutes for a rounder look.",
            "Add size and volume for a stronger lower body.",
            "Build power for better athletic movement and stability."
        ],
        "hamstrings": [
            "Increase muscle size for thicker legs.",
            "Improve tone and shape in the back of your thighs.",
            "Boost strength for sprints, lifts, and athletic performance."
        ],
        "quadriceps": [
            "Build muscle mass for fuller, stronger thighs.",
            "Highlight muscle shape and tone in the front of legs.",
            "Enhance lower-body strength for squats and jumps."
        ],
        "calves": [
            "Add muscle size for balanced leg proportions.",
            "Sculpt lean, visible lower-leg muscles.",
            "Strengthen calves for running, walking, and daily activity."
        ]
    }

    muscles = random.sample(["Biceps", "Back","Chest", "Shoulders", "Triceps","Glutes", "Hamstrings", "Quadriceps", "Calves"], 4)

    #For every muscle group selected, pick a random number from 1 to len(goals) of 
    # the muscle and then,  randomly the number of goals. 
    muscle_goals =  {}
    muscle_workout_frequency = {}
    for muscle in muscles: 

        #goals
        n_goals = random.randrange(1, len(muscle_goals[muscle]))
        goals = random.sample(muscle_goals[muscle], n_goals)
        
        muscle_goals[muscle]  = goals

        #frequency 
        frequency  = random.choice(["2-3 times/week", "4-5 times/week", "6+ times / week"])
        muscle_workout_frequency[muscle] = frequency

    time_constraint = random.choice(["short", "medium", "long"])

    if time_constraint == "short":
        workout_duration = 30
    elif time_constraint == "medium":
        workout_duration = 60
    else : 
        workout_duration = 90

    fitness_level = random.choice(["begginers", "intermediate_early", "intermediate_late"])

    if fitness_level == "begginers":
        experience_level_description = "I'm just starting out and have less than 3 months of experience." ,
    elif fitness_level == "intermediate_early":
        experience_level_description = " I've been training regularly for 1 to 2 years"
    else: 
        experience_level_description = "I've been training regularly for 2 to 3 years"


    final_user_responses = {
            "muscle_groups": muscles,
            "goals": muscle_goals,
            "muscle_workout_frequency": muscle_workout_frequency,
            "workout_duration": workout_duration,
            "time_constraint": time_constraint, 
            "fitness_level": fitness_level, 
            "experience_level_description": experience_level_description,  
        }

    return final_user_responses


def percentile(values: Sequence[float], pct: float) -> float:
    if not values:
        raise ValueError("Cannot compute percentile on empty data")
    if not 0.0 <= pct <= 1.0:
        raise ValueError("Percentile must be within [0, 1]")

    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]

    rank = (len(ordered) - 1) * pct
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[int(rank)]

    weight_upper = rank - lower
    weight_lower = 1.0 - weight_upper
    return ordered[lower] * weight_lower + ordered[upper] * weight_upper


def summarise(values: Sequence[float]) -> Optional[Dict[str, float]]:
    if not values:
        return None
    cleaned = [v for v in values if not math.isnan(v)]
    if not cleaned:
        return None

    return {
        "mean": statistics.fmean(cleaned),
        "median": statistics.median(cleaned),
        "p90": percentile(cleaned, 0.9),
        "p95": percentile(cleaned, 0.95),
        "count": float(len(cleaned)),
    }


def format_summary(label: str, stats: Optional[Dict[str, float]]) -> str:
    if not stats:
        return f"{label}: no successful samples"
    return (
        f"{label} (n={int(stats['count'])}): "
        f"mean={stats['mean']:.2f}s, median={stats['median']:.2f}s, "
        f"p90={stats['p90']:.2f}s, p95={stats['p95']:.2f}s"
    )


def run_benchmarks(
    processed_responses_list: Sequence[Dict[str, Any]],
    runs: int,
) -> None:
    workflow_durations: List[float] = []
    stage_metrics: MutableMapping[str, MutableMapping[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    scenario_count = len(processed_responses_list)
    LOGGER.info("Loaded %s processed response scenario(s).", scenario_count)

    for run_index in range(1, runs + 1):
        LOGGER.info("=== Run %s/%s ===", run_index, runs)

        workflow = WorkoutBuilderWorkflow(stream_response=True)

        scenario_index = (run_index - 1) % scenario_count
        scenario = copy.deepcopy(processed_responses_list[scenario_index])
        LOGGER.info(
            "Using scenario %s (muscle_groups=%s, duration=%s min, fitness_level=%s)",
            scenario_index + 1,
            scenario.get("muscle_groups"),
            scenario.get("workout_duration"),
            scenario.get("fitness_level"),
        )

        start = time.perf_counter()
        metadata_records: Iterable[Dict[str, Any]] = []
        try:
            result = workflow.run_workflow(scenario)
            duration = time.perf_counter() - start
            workflow_durations.append(duration)

            if isinstance(result, tuple) and len(result) == 2:
                _, metadata_records = result

            LOGGER.info("Run %s completed in %.2fs", run_index, duration)
        except Exception as exc:  # pylint: disable=broad-except
            duration = time.perf_counter() - start
            workflow_durations.append(duration)
            LOGGER.exception("Run %s failed after %.2fs: %s", run_index, duration, exc)
            metadata_records = []

        for record in metadata_records:
            if record.get("status") != "success":
                continue
            stage = str(record.get("stage", "unknown"))
            metrics = stage_metrics[stage]
            for key in ("total_time", "time_first_token", "output_gen_time", "tokens_per_second", "avg_token_per_sec"):
                value = record.get(key)
                if isinstance(value, (int, float)):
                    metrics[key].append(float(value))

    LOGGER.info("\nSummary Statistics:")
    LOGGER.info(format_summary("Workflow total time", summarise(workflow_durations)))

    for stage, metrics in stage_metrics.items():
        LOGGER.info("\nStage: %s", stage)
        for key in ("total_time", "time_first_token", "output_gen_time"):
            LOGGER.info("  %s", format_summary(key.replace("_", " "), summarise(metrics.get(key, []))))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    runs = 10
    input_path = Path("backend/data/processed_responses.json")

    if not input_path.exists():
        raise FileNotFoundError(f"Processed responses not found: {input_path}")

    processed_responses = load_processed_responses(input_path)
    processed_responses_list = normalise_processed_responses(processed_responses)
    run_benchmarks(processed_responses_list, runs)


if __name__ == "__main__":
    main()
