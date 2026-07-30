from builder.models.agent import Agent

class AgentRegistry:

    def __init__(self):
        self._agents = {}

    def register(self, name: str, role: str):
        agent = Agent(
            name=name,
            role=role,
        )
        self._agents[name] = agent
        return agent

    def get(self, name: str):
        return self._agents.get(name)

    def all(self):
        return list(self._agents.values())

    def start(self, name: str):
        agent = self._agents[name]
        agent.status = "running"
        return agent

    def stop(self, name: str):
        agent = self._agents[name]
        agent.status = "idle"
        return agent

agents = AgentRegistry()
