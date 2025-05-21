from task.task_and_store import Task


class GeneratedTask(Task):
    def __init__(self, config, description):
        self.config = config
        self.description = description