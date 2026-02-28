import multiprocessing
import traceback
import resource
import os


class SandboxExecutionError(Exception):
    pass


class SandboxTimeoutError(Exception):
    pass


def _worker(func, kwargs, queue):
    try:
        # 🔥 設定最大記憶體（例如 100MB）
        memory_limit = 100 * 1024 * 1024  # 100MB
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

        # 🔥 設定 CPU time（秒）
        cpu_limit = 2
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))

        result = func(**kwargs)
        queue.put(("success", result))

    except Exception:
        queue.put(("error", traceback.format_exc()))


class SandboxExecutor:

    def __init__(self, timeout=2):
        self.timeout = timeout

    def run(self, func, kwargs: dict):

        queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=_worker,
            args=(func, kwargs, queue)
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