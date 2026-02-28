from django.db import models
from django.utils import timezone


# =====================================================
# Organization (Multi-tenant root model)
# =====================================================
class Organization(models.Model):

    org_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    name = models.CharField(max_length=255)

    monthly_token_quota = models.IntegerField(default=10000)
    current_month_tokens = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.org_id})"

    # 🔥 可做每月 reset
    def reset_monthly_usage(self):
        self.current_month_tokens = 0
        self.save()


# =====================================================
# Generation Record
# =====================================================
class GenerationRecord(models.Model):

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="generations",
        db_index=True
    )

    module_name = models.CharField(max_length=255)

    attempts = models.IntegerField()
    total_tokens = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.org_id} - {self.module_name}"


# =====================================================
# Token Usage Log
# =====================================================
class TokenUsage(models.Model):

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="token_usages",
        db_index=True
    )

    source = models.CharField(
        max_length=50,
        choices=[
            ("generation", "Generation"),
            ("repair", "Repair"),
            ("execution", "Execution"),
        ]
    )

    tokens_used = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.org_id} - {self.source} - {self.tokens_used}"


# =====================================================
# Cost Event (Execution-level tracking)
# =====================================================
class CostEvent(models.Model):

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="cost_events",
        db_index=True,
    )

    module_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)

    token_used = models.IntegerField(default=0)
    execution_time = models.FloatField(default=0)
    cost_amount = models.FloatField(default=0)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization.org_id} - {self.module_name} - {self.event_type}"