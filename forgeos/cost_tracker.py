from forgeos.models import CostEvent


def record_event(
    org_id: str,
    module_name: str,
    event_type: str,
    token_used: int = 0,
    execution_time: float = 0,
    metadata: dict = None,
):
    """
    Centralized cost tracking entry.
    """

    if metadata is None:
        metadata = {}

    CostEvent.objects.create(
        org_id=org_id,
        module_name=module_name,
        event_type=event_type,
        token_used=token_used,
        execution_time=execution_time,
        metadata=metadata,
    )