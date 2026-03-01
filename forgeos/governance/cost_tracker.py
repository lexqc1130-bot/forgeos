from forgeos.governance.models import CostEvent, Organization


def record_event(
    org_id: str,
    module_name: str,
    event_type: str,
    token_used: int = 0,
    execution_time: float = 0,
    cost_amount: float = 0,
    metadata: dict = None
):

    if metadata is None:
        metadata = {}

    try:
        organization = Organization.objects.get(org_id=org_id)
    except Organization.DoesNotExist:
        # 如果 tenant 不存在就直接丟錯
        raise Exception(f"Organization '{org_id}' not found")

    CostEvent.objects.create(
        organization=organization,  # 🔥 改這裡
        module_name=module_name,
        event_type=event_type,
        token_used=token_used,
        execution_time=execution_time,
        cost_amount=cost_amount,
        metadata=metadata
    )