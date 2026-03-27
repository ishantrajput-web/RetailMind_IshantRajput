class ConversationMemory:
    def __init__(self, max_turns: int = 10):
        self.history = []
        self.max_turns = max_turns

    def add_user(self, message: str):
        self.history.append({"role": "user", "content": message})
        self._trim()

    def add_assistant(self, message: str):
        self.history.append({"role": "assistant", "content": message})
        self._trim()

    def get_history(self) -> list:
        return self.history.copy()

    def _trim(self):
        max_items = self.max_turns * 2
        if len(self.history) > max_items:
            self.history = self.history[-max_items:]

    def reset(self):
        self.history = []

    def has_context(self) -> bool:
        return len(self.history) > 0
