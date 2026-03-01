import multiprocessing
import traceback
import resource

class SandboxExecutionError(Exception):
    pass

class SandboxTimeoutError(Exception):
    pass


def _worker(raw_code, service_name, kwargs, queue):
    try:
        # 記憶體限制
 #       memory_limit = 100 * 1024 * 1024
 #       resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

        # CPU 限制
 #       cpu_limit = 2
 #       resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))

        # 在子 process 內 exec
        namespace = {}
        safe_globals = {
            "__builtins__": {
                "len": len,
                "range": range,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "isinstance": isinstance,
            }
        }

        exec(raw_code, safe_globals, namespace)

        if service_name not in namespace:
            raise Exception(f"Service '{service_name}' not found")

        result = namespace[service_name](**kwargs)

        queue.put(("success", result))

    except Exception:
        queue.put(("error", traceback.format_exc()))


class SandboxExecutor:

    def __init__(self, timeout=2):
        self.timeout = timeout

    def run(self, module, service_name, kwargs):

        if not hasattr(module, "raw_code"):
            raise SandboxExecutionError("Module has no raw_code")

        queue = multiprocessing.Queue()

        process = multiprocessing.Process(
            target=_worker,
            args=(module.raw_code, service_name, kwargs, queue)
        )

        process.start()
        process.join(self.timeout)

        if process.is_alive():
            process.terminate()
            process.join()
            raise SandboxTimeoutError("Execution timed out")

        if queue.empty():
            raise SandboxExecutionError("No result returned")

        status, payload = queue.get()

        if status == "error":
            raise SandboxExecutionError(payload)

        return payload