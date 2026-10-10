class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, description, parameters, function):
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "function": function,
        }

    def get(self, name):
        return self.tools.get(name)

    def list_tools(self):
        return list(self.tools.values())

    def get_tool_schemas(self):
        schemas = []

        for tool in self.tools.values():
            schemas.append({
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
            })

        return schemas

    def execute(self, name, arguments):
        tool = self.get(name)

        if tool is None:
            return {
                "success": False,
                "error": f"Unknown tool: {name}",
            }

        try:
            result = tool["function"](**arguments)

            return {
                "success": True,
                "result": result,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }