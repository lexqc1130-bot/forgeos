from .models import CostEvent


def record_event(
    org_id: str,
    module_name: str,
    event_type: str,
    execution_time: float = 0,
    token_used: int = 0,
    metadata: dict = None,
    cost_amount: float = 0,
):
    if metadata is None:
        metadata = {}

    CostEvent.objects.create(
        org_id=org_id,
        module_name=module_name,
        event_type=event_type,
        execution_time=execution_time,
        token_used=token_used,
        cost_amount=cost_amount,
        metadata=metadata,
    )