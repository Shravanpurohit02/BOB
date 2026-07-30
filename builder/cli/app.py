import typer

from builder.core import environment, queue, state
from builder.core.session import load_session

runtime = load_session()
from builder.core.queue_worker import worker as queue_worker
from builder.core.checkpoints import create_checkpoint
from builder.version import __title__, __version__

app = typer.Typer(add_completion=False, invoke_without_command=True)

@app.callback()
def root():
    print(f"{__title__} {__version__}")
    print(f"Session     : {runtime.session_id}")
    print(f"Workspace   : {runtime.workspace}")
    print(f"Project     : {runtime.project.name}")
    print(f"Detected    : {runtime.project.detected}")
    print(f"PyProject   : {runtime.project.pyproject is not None}")
    print(f"Git         : {runtime.project.git is not None}")
    print(f"Python      : {environment.python_version}")
    print(f"Platform    : {environment.platform_name}")
    print(f"Termux      : {environment.termux}")
    print(f"Boot Count  : {state.boot_count}")
    print(f"Queue Size  : {len(queue)}")

@app.command()
def checkpoint(name: str, description: str = ""):
    cp = create_checkpoint(name, description)
    print(cp.id)

@app.command()
def task(name: str):
    t = queue.submit(name)
    print(t.id)



@app.command()
def status():

    import json
    from pathlib import Path

    task_file = Path(".builder/state/tasks.json")
    change_dir = Path(".builder/state/changesets")

    tasks = []

    if task_file.exists():
        tasks = json.loads(task_file.read_text(encoding="utf-8"))

    total = len(tasks)
    pending = sum(t.get("status") == "pending" for t in tasks)
    running = sum(t.get("status") == "running" for t in tasks)
    completed = sum(t.get("status") == "completed" for t in tasks)
    failed = sum(t.get("status") == "failed" for t in tasks)

    changesets = list(change_dir.glob("*.json")) if change_dir.exists() else []

    print("=" * 70)
    print("VIDHI BUILDER STATUS")
    print("=" * 70)
    print("Project        :", runtime.project.name)
    print("Workspace      :", runtime.workspace)
    print("Session        :", runtime.session_id)
    print("Version        :", __version__)
    print("Python         :", environment.python_version)
    print("Platform       :", environment.platform_name)
    print("Termux         :", environment.termux)
    print("Git            :", runtime.project.git is not None)
    print("PyProject      :", runtime.project.pyproject is not None)
    print("-" * 70)
    print("Queue          :", len(queue))
    print("Tasks          :", total)
    print("Pending        :", pending)
    print("Running        :", running)
    print("Completed      :", completed)
    print("Failed         :", failed)
    print("Changesets     :", len(changesets))
    print("=" * 70)


@app.command()
def run(objective: str):

    from pathlib import Path

    from builder.orchestrator.engine import engine
    from builder.orchestrator.request import BuildRequest

    print("=" * 70)
    print("VIDHI BUILDER")
    print("=" * 70)
    print("Objective :", objective)
    print()

    result = engine.run(
        BuildRequest(
            objective=objective,
            workspace=str(Path.cwd()),
        )
    )

    print("Pipeline   :", result["pipeline"].success)
    print("Execution  :", result["execution"].success)
    print("Runtime    :", result["runtime"].success)
    print("Generation :", result["generation"].success)
    print("Changeset  :", result["changeset"].id)

    print()
    print("Stages")
    print("-" * 70)

    for stage in result["pipeline"].stages:
        print("✓", stage)

    print("-" * 70)
    print("SUCCESS" if result["runtime"].success else "FAILED")
    print("=" * 70)
