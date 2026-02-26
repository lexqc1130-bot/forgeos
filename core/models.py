from django.db import models


class ForgeModuleRecord(models.Model):
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name