import json
from dataclasses import asdict
from pathlib import Path

from builder.models.plan import Plan

PLAN_FILE = Path(".builder/state/plans.json")

class PlanManager:
    def __init__(self):
        self._plans = {}
        self._load()

    def _load(self):
        if PLAN_FILE.exists():
            self._plans = {
                p["id"]: Plan(**p)
                for p in json.loads(
                    PLAN_FILE.read_text(encoding="utf-8")
                )
            }

    def _save(self):
        PLAN_FILE.parent.mkdir(parents=True, exist_ok=True)
        PLAN_FILE.write_text(
            json.dumps(
                [asdict(p) for p in self._plans.values()],
                indent=2,
            ),
            encoding="utf-8",
        )

    def create(self, name: str, goal: str):
        plan = Plan(name=name, goal=goal)
        self._plans[plan.id] = plan
        self._save()
        return plan

    def add_job(self, plan_id: str, job_id: str):
        self._plans[plan_id].jobs.append(job_id)
        self._save()

    def start(self, plan_id: str):
        self._plans[plan_id].status = "running"
        self._save()

    def complete(self, plan_id: str):
        self._plans[plan_id].status = "completed"
        self._save()

    def all(self):
        return list(self._plans.values())

plans = PlanManager()
