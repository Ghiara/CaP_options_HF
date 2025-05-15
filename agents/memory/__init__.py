from agents.memory.config_manager import ConfigManager
from agents.memory.examples_manager import ExamplesManager
from agents.memory.skill_manager import SkillManager
from agents.model import Skill, TaskExample, EnvironmentConfiguration, InteractionTrace

import os
import pickle



class MemoryManager:
    """
    Initialises agent memory at a given root directory, creating folders and the required sub memory modules.
    If an agent already exists at the given directory, just gets this one. Otherwise initialises a new agent.
    Also wraps the most common functions for more concise access (in retrospect maybe not a great decision).
    """
    def __init__(self, root_dir):
        should_init_memory = False
        if not os.path.isdir(root_dir):
            os.makedirs(root_dir, exist_ok=True)
            should_init_memory = True

        self.skill_manager = SkillManager(root_dir)
        self.config_manager = ConfigManager(root_dir)
        self.example_manager = ExamplesManager(
            root_dir, config_manager=self.config_manager
        )

        if should_init_memory:
            self.init_examples_and_skills()

        self.EXPERIENCE_DIR = os.path.join(root_dir, "trajectories")
        os.makedirs(self.EXPERIENCE_DIR, exist_ok=True)

    def init_examples_and_skills(self):
        """adds examples and skills for an agent initialised at a new memory directory"""
        self.skill_manager.add_core_primitives_to_library()
        from utils.base_examples import base_task_examples

        examples = base_task_examples()
        for example in examples:
            print(f"adding example: {example.task}")
            self.add_example(example)

    def add_skill(self, skill: Skill):
        self.skill_manager.add_skill_to_library(skill)

    def add_example(self, example: TaskExample):
        self.example_manager.add_example_to_library(example)

    def retrieve_skills(self, query, num_results=5) -> list[Skill]:
        return self.skill_manager.retrieve_skills(query, num_results=num_results)

    def retrieve_examples(self, query, num_results=5) -> list[TaskExample]:
        return self.example_manager.retrieve_similar_examples(
            query, num_results=num_results
        )

    def retrieve_configs(self, query, num_results=5) -> list[EnvironmentConfiguration]:
        """returns similar stored environment configs"""
        return self.config_manager.retrieve_configs(query, num_results=num_results)

    def skill_task_examples(self, skill: Skill) -> list[TaskExample]:
        """returns the examples generated while learning a skill"""
        return [
            self.example_manager.retrieve_task_with_id(id)
            for id in skill._task_examples
        ]

    def add_trace(self, trace: InteractionTrace):
        trace.dump(self.EXPERIENCE_DIR)

    def get_all_traces(self) -> list[InteractionTrace]:
        traces = []
        for pickle_file in os.listdir(self.EXPERIENCE_DIR):
            with open(f"{self.EXPERIENCE_DIR}/{pickle_file}", "rb") as file:
                trace = pickle.load(file)
                traces.append(trace)
        return traces