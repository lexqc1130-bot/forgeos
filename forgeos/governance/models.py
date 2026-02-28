from django.db import models
from django.utils import timezone


class CostEvent(models.Model):
    org_id = models.CharField(max_length=100)
    module_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=100)

    token_used = models.IntegerField(default=0)
    execution_time = models.FloatField(default=0)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.module_name} - {self.event_type}"