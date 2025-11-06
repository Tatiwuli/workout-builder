from ..database.mongodb_handler import WorkoutBuilderDatabaseHandler
from ..utils.agent_utils import combine_texts


class WorkoutKnowledgeFetch:
    def __init__(self):
        self.db_handler = WorkoutBuilderDatabaseHandler()

    def fetch_fitness_level_wiki(self, fitness_level, time_constraint):
        wiki_doc = self.db_handler.fetch_data(
            collection_name="wikis", query={"wiki_name": "wiki_by_fitness_level"}
        )
        if not wiki_doc:
            raise ValueError("No document found with wiki_name 'wiki_by_fitness_level'.")

        fitness_levels = wiki_doc[0].get("fitness_levels", {})
        specific_fitness_level = fitness_levels.get(fitness_level, {})

        if not specific_fitness_level:
            raise ValueError(f"Fitness level '{fitness_level}' not found in wiki.")

        time_constraints = specific_fitness_level.get("time_constraints", {})
        specific_time_constraint = time_constraints.get(time_constraint, {})

        if not specific_time_constraint:
            raise ValueError(f"Time constraint '{time_constraint}' not found for fitness level '{fitness_level}'.")

        filtered_wiki_data = {
            "fitness_level": fitness_level,
            "time_constraint": time_constraint,
            "rationale": specific_fitness_level.get("rationale", ""),
            "exercise_selection": specific_fitness_level.get("exercise_selection", []),
            "n_exercises": specific_fitness_level.get("n_exercises", ""),
            "sets": specific_fitness_level.get("sets", ""),
            "reps": specific_fitness_level.get("reps", ""),
            "time_constraint_guidelines": specific_time_constraint
        }

        return combine_texts([filtered_wiki_data])

    def fetch_muscle_group_wiki(self, muscle_groups):
        wiki_doc = self.db_handler.fetch_data(
            collection_name="wikis", query={"wiki_name": "wiki_by_muscle_group"}
        )
        if not wiki_doc:
            raise ValueError("No document found with wiki_name 'wiki_by_muscle_group'.")

        key_principles = {}
        for muscle_group in muscle_groups:
            matching_sections = [
                section for section in wiki_doc[0].get("sections", [])
                if muscle_group in section.get("muscle_groups", [])
            ]
            key_principles[muscle_group] = {
                "key_principles": wiki_doc[0].get("key_principles", []),
                "sections": matching_sections,
            }
        return key_principles

    def extract_exercises_summary(self, muscle_groups):
        video_documents = self.db_handler.fetch_data(
            collection_name="videos_summaries",
            query={"video_targeted_muscle_groups": {"$in": muscle_groups}},
        )
        return [
            doc.get("exercises_summary", {}) for doc in video_documents if "exercises_summary" in doc
        ]

    def extract_main_knowledge_summary(self, muscle_groups):
        video_documents = self.db_handler.fetch_data(
            collection_name="videos_summaries",
            query={"video_targeted_muscle_groups": {"$in": muscle_groups}},
        )
        return [
            doc.get("main_knowledge_summary", {}) for doc in video_documents
        ]

