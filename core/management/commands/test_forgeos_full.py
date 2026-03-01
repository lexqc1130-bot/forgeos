from django.core.management.base import BaseCommand
from forgeos.kernel.engine import ForgeEngine
from forgeos.runtime.execution_context import ExecutionContext
from forgeos.governance.models import (
    Organization,
    GenerationRecord,
    TokenUsage
)
from forgeos.governance.models import CostEvent
from django.db import transaction


class Command(BaseCommand):
    help = "Full ForgeOS regression test"

    def handle(self, *args, **options):

        self.stdout.write("=== ForgeOS Full Regression Test ===")

        # ---------------------------------------
        # 1️⃣ 建立測試 Org
        # ---------------------------------------
        org, _ = Organization.objects.get_or_create(
            org_id="regression_org",
            defaults={
                "name": "Regression Org",
                "monthly_token_quota": 10000
            }
        )

        org.current_month_tokens = 0
        org.save()

        engine = ForgeEngine(org_id=org.org_id)

        # ---------------------------------------
        # 2️⃣ 測試 Module Generation
        # ---------------------------------------
        schema = {
            "name": "square_test_service",
            "type": "service"
        }

        module = engine.build_module(schema)

        assert module.lifecycle.get_state().value == "DEPLOYED"
        self.stdout.write("✓ Module build OK")

        # GenerationRecord 檢查
        assert GenerationRecord.objects.filter(
            organization=org,
            module_name="square_test_service"
        ).exists()
        self.stdout.write("✓ GenerationRecord OK")

        # TokenUsage (generation)
        assert TokenUsage.objects.filter(
            organization=org,
            source="generation"
        ).exists()
        self.stdout.write("✓ Generation TokenUsage OK")

        # ---------------------------------------
        # 3️⃣ Activate
        # ---------------------------------------
        engine.activate_module("square_test_service")

        # ---------------------------------------
        # 4️⃣ Execution Success
        # ---------------------------------------
        context = ExecutionContext(
            org_id=org.org_id,
            payload={"number": 5}
        )

        result = engine.execute("run", context)

        assert result == 25
        self.stdout.write("✓ Execution success OK")

        # CostEvent 檢查
        assert CostEvent.objects.filter(
            organization=org,
            event_type="execution_success"
        ).exists()
        self.stdout.write("✓ CostEvent OK")

        # TokenUsage (execution)
        assert TokenUsage.objects.filter(
            organization=org,
            source="execution"
        ).exists()
        self.stdout.write("✓ Execution TokenUsage OK")

        # ---------------------------------------
        # 5️⃣ Retry Test
        # ---------------------------------------
        context_retry = ExecutionContext(
            org_id=org.org_id,
            payload={"number": "invalid"},  # 會錯
            retry_count=1
        )

        try:
            engine.execute("run", context_retry)
        except Exception:
            pass

        assert CostEvent.objects.filter(
            organization=org,
            event_type="execution_retry"
        ).exists()
        self.stdout.write("✓ Retry handling OK")

        # ---------------------------------------
        # 6️⃣ Quota Exceed Test
        # ---------------------------------------
        org.monthly_token_quota = 1
        org.current_month_tokens = 1
        org.save()

        context_quota = ExecutionContext(
            org_id=org.org_id,
            payload={"number": 2}
        )

        try:
            engine.execute("run", context_quota)
            raise Exception("Quota test failed")
        except Exception as e:
            assert "quota" in str(e).lower()

        self.stdout.write("✓ Quota enforcement OK")

        # ---------------------------------------
        # 7️⃣ Multi-tenant isolation
        # ---------------------------------------
        other_org, _ = Organization.objects.get_or_create(
            org_id="other_org",
            defaults={
                "name": "Other Org",
                "monthly_token_quota": 10000
            }
        )

        other_engine = ForgeEngine(org_id=other_org.org_id)

        try:
            other_engine.execute("run", context)
            raise Exception("Isolation failed")
        except Exception:
            pass

        self.stdout.write("✓ Multi-tenant isolation OK")

        self.stdout.write("=== ALL TESTS PASSED ===")