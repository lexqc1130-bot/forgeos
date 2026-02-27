from django.db import models


class ModuleRecord(models.Model):
    org_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)

    state = models.CharField(max_length=50)
    schema_json = models.JSONField()

    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("org_id", "name", "version")

    def __str__(self):
        return f"{self.org_id} - {self.name} - {self.version}"