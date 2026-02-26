from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ForgeModuleSchema:
    name: str
    type: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)

    def validate(self):
        if not self.name:
            raise ValueError("Module must have a name")
        if not self.type:
            raise ValueError("Module must have a type")
        return True