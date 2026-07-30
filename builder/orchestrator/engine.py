from .orchestrator import orchestrator

class OrchestratorEngine:

    def run(self, request):
        return orchestrator.execute(request)

engine = OrchestratorEngine()
