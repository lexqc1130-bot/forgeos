from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ExecutionContext:
    org_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    strategy: str = "first"

    # Retry settings
    retry_count: int = 0
    retry_delay: float = 0
    backoff_multiplier: float = 1.0