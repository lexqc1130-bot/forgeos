from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ExecutionContext:
    """
    Context object passed into execution engine.

    Future:
    - Agent layer will enrich this.
    - Add tracing, cost budget, decision hints.
    """

    org_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    strategy: str = "first"   # first / random / cheapest (future)