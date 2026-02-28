from enum import Enum


class ModuleState(Enum):
    INIT = "INIT"
    GENERATED = "GENERATED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"
    REPAIRED = "REPAIRED"
    DEPLOYED = "DEPLOYED"


class ModuleLifecycle:
    def __init__(self):
        self.state = ModuleState.INIT
        self.history = []

    def transition(self, new_state: ModuleState):
        self.history.append((self.state, new_state))
        self.state = new_state

    def get_state(self):
        return self.state

    def get_history(self):
        return self.history

    # 🔥 新增這個方法（關鍵）
    def to_dict(self):
        return {
            "state": self.state.value,
            "history": [
                {
                    "from": old.value,
                    "to": new.value
                }
                for old, new in self.history
            ]
        }