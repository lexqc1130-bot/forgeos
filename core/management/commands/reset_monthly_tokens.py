from django.core.management.base import BaseCommand
from forgeos.governance.models import Organization


class Command(BaseCommand):
    help = "Reset monthly token usage for all organizations"

    def handle(self, *args, **options):

        Organization.objects.update(current_month_tokens=0)

        self.stdout.write("✅ All organizations monthly tokens reset.")