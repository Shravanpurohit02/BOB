from builder.execution.snapshot import engine, recovery


def run():

    snapshot = engine.create(
        transaction_id="tx-regression",
        execution_id="exec-regression",
        objective="Execution Snapshot Regression",
        workspace=".",
    )

    engine.checkpoint(
        snapshot,
        "planning",
    )

    engine.complete_stage(
        snapshot,
        "planning",
    )

    loaded = engine.load(snapshot.id)

    if loaded is None:
        return False

    report = recovery.validate(
        loaded,
    )

    if not report["valid"]:
        return False

    if len(loaded.checkpoints) != 1:
        return False

    if loaded.checkpoints[0].status != "completed":
        return False

    deleted = engine.delete(
        snapshot.id,
    )

    return (
        deleted
        and engine.load(snapshot.id) is None
    )
