from task.task_and_store import Task


class PlaceGreenNextToYellow(Task):
    def __init__(self):
        super().__init__()
        self.lang_goal = "place the green block next to the yellow block"
        self.identifier = "place-2-blocks"

    def reset(self, env):
        super().reset(env)
        self.add_block(env, "green")
        self.add_block(env, "yellow")

