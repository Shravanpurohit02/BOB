from __future__ import annotations

from builder.config import settings
import json
import os
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from builder.ast.module import Module
from builder.engineering.transaction.serializer import serializer


class ASTCache:
    def __init__(self, root=None):
        self.root = Path(root) if root else settings.resolve_runtime_directory() / "ast"
        self.root.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.root / "metadata.json"
        self.modules_file = self.root / "modules.json"

    def _atomic_write(self, target, text):
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=str(target.parent), delete=False
        ) as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
            name = f.name
        os.replace(name, target)

    def _load_json(self, path, default):
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            try:
                path.unlink()
            except Exception:
                pass
            return default

    def _save_json(self, path, obj):
        self._atomic_write(path, serializer.dumps(obj))

    @staticmethod
    def fingerprint(path):
        s = Path(path).stat()
        return {"mtime_ns": s.st_mtime_ns, "size": s.st_size}

    @staticmethod
    def normalize(path):
        return str(Path(path).resolve()).replace("\\", "/")

    def load(self):
        meta = self._load_json(self.metadata_file, {})
        raw = self._load_json(self.modules_file, {})
        mods = {}
        for k, v in raw.items():
            try:
                mods[k] = Module(**v)
            except Exception:
                pass
        return meta, mods

    def save(self, meta, mods):
        self._save_json(self.metadata_file, meta)
        self._save_json(self.modules_file, {k: asdict(v) for k, v in mods.items()})

    def classify(self, files):
        meta, mods = self.load()
        current = {self.normalize(f): Path(f) for f in files}
        stale = []
        for k in list(mods):
            if k not in current:
                mods.pop(k, None)
                meta.pop(k, None)
        for k, p in current.items():
            if meta.get(k) != self.fingerprint(p):
                stale.append(p)
        return meta, mods, stale

    def update(self, meta, mods, parsed):
        for m in parsed:
            k = self.normalize(m.path)
            mods[k] = m
            meta[k] = self.fingerprint(m.path)
        self.save(meta, mods)
        return list(mods.values())


cache = ASTCache()
