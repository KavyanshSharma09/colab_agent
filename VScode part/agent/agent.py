from session import Session
from agent.loop import run_agent
from runtime import RuntimeContext


class Agent:

    def __init__(self, registry, context=None, model=None):
        self.registry = registry
        self.context = context or RuntimeContext()
        self.session = Session(self.context)
        self.model = model

    def run(self, task):
        """
        Run the agent on a user task.
        """

        self.session.start_turn(task)

        return run_agent(
            self.session,
            self.registry,
            model=self.model,
        )

    def reset(self):
        """
        Clear the current session.
        """

        self.session.clear()

    def get_session(self):
        """
        Return the current session.
        """

        return self.session