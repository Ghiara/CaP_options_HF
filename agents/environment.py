from task.task_and_store import Task, GeneratedTask
from agents.model import EnvironmentConfiguration
from environments.environment import Environment
from agents.memory import MemoryManager
from prompts.task_gen_prompt import task_setup_system_prompt
from utils.llm_utils import query_llm, parse_code_response

from task.sample_tasks import Place2Blocks


class EnvironmentAgent:
    """
    responsible for aiding in environment setup
    like the actor, should get better and better at setting the environment to a specific configuration
    for now just a two-pass attempt
    first: retrieve previous configs
    if none chosen, generate new from string

    THE TASK STRING SHOULDN'T BE PART OF THIS! relic of the Cliport repo, and associated Task class...
    """

    def __init__(self, memory_manager: MemoryManager):
        self.is_recording = False

        self.current_task = Task()
        self.setup_environment()
        self.reset()
        self.memory_manager = memory_manager

    def parse_predefined_task(self, identifier):
        self.current_task = get_task_with_identifier(identifier)

    def parse_task_dummy(self):
        self.current_task = Place2Blocks()

    def parse_task(self):
        task_str = input("give the task to be solved:\n")
        task = self.parse_env_setup()
        task.set_lang_goal(task_str)
        self.current_task = task

    def parse_env_setup(self, allow_existing_configs: bool = False):
        env_setup_prompt = input(
            "how should the environment be set up? ('keep' for same setup)\n"
        )

        if env_setup_prompt == "keep":
            return self.current_task
        elif env_setup_prompt == "none":
            task = Task()
            return task

        if allow_existing_configs:
            existing_configs = self.memory_manager.retrieve_configs(
                env_setup_prompt, num_results=10
            )
            print(
                f"existing configs\n {'\n'.join([config.description for config in existing_configs])}"
            )
            use_existing_config = input(
                "use existing config? (provide index of config or none if don't want to use) \n"
            )

            if use_existing_config != "none":
                config = existing_configs[int(use_existing_config)]
                task = GeneratedTask()
                task.set_config(config)

                modify_config = input("modify the config? (prompt or none)")

                if modify_config != "none":
                    setup_code = self.generate_task_setup_code(modify_config)
                    task.set_task_setup_code(setup_code)

                return task

        task = GeneratedTask()
        setup_code = self.generate_task_setup_code(env_setup_prompt)
        print(setup_code)
        task.set_task_setup_code(setup_code)
        return task

    def setup_environment(self):
        from pathlib import Path
        from datetime import datetime

        video_save_dir = Path(__file__).parent.parent / "data"
        env = Environment(
            "/Users/maxfest/vscode/thesis/thesis/environments/assets",
            disp=True,
            shared_memory=False,
            hz=480,
            record_cfg={
                "save_video": self.is_recording,
                "save_video_path": video_save_dir,
                "add_text": False,
                "add_task_text": False,
                "fps": 20,
                "video_height": 640,
                "video_width": 720,
            },
        )

        self.env = env

    def reset(self):
        self.env.set_task(self.current_task)
        self.env.reset()
        config = self.get_current_config()
        self.config_stack = [config]

        if self.is_recording:
            from datetime import datetime

            video_file_name = datetime.now().strftime("%d_%H-%M-%S")
            self.env.start_rec(video_file_name)

        return config

    def pop_config(self) -> EnvironmentConfiguration:
        # TODO: this function should enable the user to solve a task in steps, 
        # rather than generating the entire solution code in one go
        # while simple in principle, actually generating code in a manner that enables this is not trivial
        # would definitely be a useful function though

        config = self.configs[-1]
        self.set_to_task_and_config(self.current_task.lang_goal, config)

    def get_current_config(self) -> EnvironmentConfiguration:
        return self.env.task.get_current_configuration(self.env)

    def set_to_task_and_config(self, task: str, config: EnvironmentConfiguration):
        reset_task = Task()
        reset_task.config = config
        reset_task.lang_goal = task
        self.current_task = reset_task
        self.reset()

    def set_task(self, task: Task):
        self.current_task = task

    def generate_task_setup_code(self, task_setup_prompt: str):
        messages = [
            {"role": "system", "content": task_setup_system_prompt},
            {"role": "user", "content": task_setup_prompt},
        ]

        response = query_llm(messages)
        code = parse_code_response(response)
        return code



if __name__ == "__main__":
    import time

    env_agent = EnvironmentAgent(MemoryManager(root_dir="memory/memory"))

    env_agent.parse_task()

    env_agent.reset()

    time.sleep(10)
