import json
from dataclasses import asdict
from pathlib import Path

from builder.models.job import Job

JOB_FILE = Path(".builder/state/jobs.json")

class JobManager:

    def __init__(self):
        self._jobs = {}
        self._load()

    def _load(self):
        if JOB_FILE.exists():
            self._jobs = {
                j["id"]: Job(**j)
                for j in json.loads(JOB_FILE.read_text(encoding="utf-8"))
            }

    def _save(self):
        JOB_FILE.parent.mkdir(parents=True, exist_ok=True)
        JOB_FILE.write_text(
            json.dumps(
                [asdict(j) for j in self._jobs.values()],
                indent=2,
            ),
            encoding="utf-8",
        )

    def create(self, name: str, worker: str, **payload):
        job = Job(
            name=name,
            worker=worker,
            payload=payload,
        )
        self._jobs[job.id] = job
        self._save()
        return job

    def start(self, job_id: str):
        self._jobs[job_id].status = "running"
        self._save()
        return self._jobs[job_id]

    def complete(self, job_id: str):
        self._jobs[job_id].status = "completed"
        self._save()
        return self._jobs[job_id]

    def all(self):
        return list(self._jobs.values())

jobs = JobManager()
