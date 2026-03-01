from django.core.management.base import BaseCommand
from forgeos.kernel.engine import ForgeEngine
from forgeos.runtime.execution_context import ExecutionContext
from forgeos.governance.models import Organization


class Command(BaseCommand):
    help = "Multi-org stress test"

    def handle(self, *args, **options):

        self.stdout.write("🚀 Starting Multi-Org Stress Test")

        org_ids = ["orgA", "orgB", "orgC"]

        for org_id in org_ids:

            org, _ = Organization.objects.get_or_create(
                org_id=org_id,
                defaults={
                    "name": org_id,
                    "monthly_token_quota": 10000
                }
            )

            engine = ForgeEngine(org_id=org_id)

            schema = {
                "name": f"{org_id}_square_service",
                "type": "service"
            }

            module = engine.build_module(schema)
            engine.activate_module(schema["name"])

            context = ExecutionContext(
                org_id=org_id,
                payload={"number": 5}
            )

            result = engine.execute("run", context)

            self.stdout.write(
                f"✅ {org_id} result: {result}"
            )

        self.stdout.write("🔥 Multi-org test complete")