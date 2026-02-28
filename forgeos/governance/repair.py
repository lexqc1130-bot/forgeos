from .error_classifier import ErrorClassifier
from ..runtime.context_enhancer import ContextEnhancer
from ..kernel.lifecycle import ModuleState


class RepairStrategy:

    def apply(self, module, context):
        raise NotImplementedError


class RetryStrategy(RepairStrategy):

    def apply(self, module, context):
        module.lifecycle.transition(ModuleState.REPAIRED)
        return module


class RepairEngine:

    def __init__(self):
        self.classifier = ErrorClassifier()
        self.enhancer = ContextEnhancer()

        self.strategies = {
            "SYNTAX_ERROR": RetryStrategy(),
            "IMPORT_ERROR": RetryStrategy(),
            "DEPENDENCY_ERROR": RetryStrategy(),
            "VALIDATION_ERROR": RetryStrategy(),
            "UNKNOWN_ERROR": RetryStrategy(),
        }

    def repair(self, module, error):

        if not module.can_retry():
            raise Exception("Max repair attempts reached")

        module.retry_count += 1

        error_type = self.classifier.classify(error)
        context = self.enhancer.enhance(module, error_type)

        module.log_repair(error_type, context)

        strategy = self.strategies.get(error_type)

        if not strategy:
            raise Exception("No repair strategy available")

        return strategy.apply(module, context)