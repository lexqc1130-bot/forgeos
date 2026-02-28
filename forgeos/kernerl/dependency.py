class DependencyGraph:
    def __init__(self):
        self.graph = {}

    def add_module(self, module_name, dependencies):
        self.graph[module_name] = dependencies

    def validate(self):
        visited = set()
        stack = set()

        def visit(node):
            if node in stack:
                raise Exception(f"Circular dependency detected: {node}")
            if node not in visited:
                stack.add(node)
                for dep in self.graph.get(node, []):
                    visit(dep)
                stack.remove(node)
                visited.add(node)

        for module in self.graph:
            visit(module)

        return True

    def get_graph(self):
        return self.graph