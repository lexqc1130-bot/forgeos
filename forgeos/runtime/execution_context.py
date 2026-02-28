from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ExecutionContext:
    org_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    strategy: str = "first"

    retry_count: int = 0       # 🔥 新增
    retry_delay: float = 0     # 🔥 新增（秒）