import hashlib
from pathlib import Path

class Manifest:

    def create(self, archive: Path):

        return {
            "name": archive.name,
            "size": archive.stat().st_size,
            "sha256": hashlib.sha256(
                archive.read_bytes()
            ).hexdigest(),
        }

manifest = Manifest()
