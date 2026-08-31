from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


class ContextCache:
    def __init__(self):
        self._cache = {}
        self._root = Path(".builder") / "cache"
        self._root.mkdir(parents=True, exist_ok=True)

    def _canonical_workspace(self, workspace):
        return str(Path(workspace).resolve())

    def _key(self, workspace, objective):
        workspace = self._canonical_workspace(workspace)
        return hashlib.sha256(f"{workspace}:{objective}".encode()).hexdigest()

    def _workspace_hash(self, workspace):
        workspace = self._canonical_workspace(workspace)
        return hashlib.sha256(workspace.encode()).hexdigest()[:16]

    def _objective_hash(self, objective):
        return hashlib.sha256(objective.encode()).hexdigest()[:16]

    def _cache_file(self, workspace, objective):
        return (
            self._root
            / f"{self._workspace_hash(workspace)}_{self._objective_hash(objective)}.json"
        )

    def _load_disk(self, workspace, objective):
        p = self._cache_file(workspace, objective)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            try:
                p.unlink()
            except Exception:
                pass
            return None

    def _save_disk(self, workspace, objective, entry):
        self._cache_file(workspace, objective).write_text(
            json.dumps(entry, indent=2, sort_keys=True), encoding="utf-8"
        )

    def _delete_disk(self, workspace, objective):
        try:
            self._cache_file(workspace, objective).unlink()
        except FileNotFoundError:
            pass

    def get(self, workspace, objective, fingerprint=None):
        key = self._key(workspace, objective)
        entry = self._cache.get(key)
        if entry is None:
            entry = self._load_disk(workspace, objective)
            if entry is not None:
                self._cache[key] = entry
        if entry is None:
            return None
        if fingerprint is not None and entry.get("fingerprint") != fingerprint:
            self._cache.pop(key, None)
            self._delete_disk(workspace, objective)
            return None
        return entry

    def put(self, workspace, objective, value, fingerprint=None):
        key = self._key(workspace, objective)
        entry = {
            "created": time.time(),
            "workspace": workspace,
            "objective": objective,
            "fingerprint": fingerprint,
            "value": value,
        }
        self._cache[key] = entry
        self._save_disk(workspace, objective, entry)
        return value

    def invalidate(self, workspace=None, objective=None):
        if workspace is None:
            self._cache.clear()
            for f in self._root.glob("*.json"):
                try:
                    f.unlink()
                except Exception:
                    pass
            return
        self._cache.pop(self._key(workspace, objective), None)
        self._delete_disk(workspace, objective)

    def size(self):
        return len(self._cache)


cache = ContextCache()
