from django.core.management.base import BaseCommand
from forgeos.kernel.engine import ForgeEngine
from forgeos.runtime.execution_context import ExecutionContext
from forgeos.governance.models import Organization, CostEvent


class Command(BaseCommand):
    help = "Test ForgeOS end-to-end flow"

    def handle(self, *args, **options):

        self.stdout.write("🚀 Starting ForgeOS test...")

        # 1️⃣ 建立或取得 Organization
        org, created = Organization.objects.get_or_create(
            org_id="default_org",
            defaults={
                "name": "Default Org",
                "monthly_token_quota": 10000
            }
        )

        if created:
            self.stdout.write("✅ Organization created")
        else:
            self.stdout.write("ℹ️ Organization already exists")

        # 2️⃣ 建立 Engine
        engine = ForgeEngine(org_id=org.org_id)

        # 3️⃣ 建立 Module
        schema = {
            "name": "create a service that squares a number",
            "type": "service"
        }

        module = engine.build_module(schema)
        engine.activate_module(schema["name"])

        self.stdout.write("✅ Module built & activated")

        # 4️⃣ 建立 Execution Context
        context = ExecutionContext(
            org_id=org.org_id,
            payload={"number": 9}
        )

        # 5️⃣ 執行
        result = engine.execute("run", context)

        self.stdout.write(f"🎯 Execution result: {result}")

        # 6️⃣ 顯示 CostEvent 數量
        total_events = CostEvent.objects.count()
        self.stdout.write(f"💰 Total CostEvents: {total_events}")

        self.stdout.write("🔥 ForgeOS test completed successfully.")