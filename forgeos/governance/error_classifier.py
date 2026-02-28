class ErrorType:
    SYNTAX = "SYNTAX_ERROR"
    IMPORT = "IMPORT_ERROR"
    DEPENDENCY = "DEPENDENCY_ERROR"
    VALIDATION = "VALIDATION_ERROR"
    UNKNOWN = "UNKNOWN_ERROR"


class ErrorClassifier:

    def classify(self, error: Exception) -> str:
        msg = str(error)

        if "SyntaxError" in msg:
            return ErrorType.SYNTAX

        if "ImportError" in msg or "ModuleNotFoundError" in msg:
            return ErrorType.IMPORT

        if "dependency" in msg.lower():
            return ErrorType.DEPENDENCY

        if "validate" in msg.lower():
            return ErrorType.VALIDATION

        return ErrorType.UNKNOWN