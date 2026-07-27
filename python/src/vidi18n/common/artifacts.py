import hashlib
import os
from pathlib import Path

from vidi18n.common.settings import DATA_ROOT


class ArtifactStore:
    def __init__(self, root: str = DATA_ROOT):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, data: bytes, suffix: str = "") -> dict:
        digest = hashlib.sha256(data).hexdigest()
        path = self.root / "artifacts" / "sha256" / digest[:2] / digest[2:4]
        path.mkdir(parents=True, exist_ok=True)
        target = path / f"{digest}{suffix}"
        if not target.exists():
            temporary = target.with_suffix(target.suffix + ".tmp")
            temporary.write_bytes(data)
            os.replace(temporary, target)
        return {
            "id": f"sha256:{digest}",
            "sha256": digest,
            "size": len(data),
            "path": str(target),
        }

    def put_file(self, source: str, suffix: str = "") -> dict:
        return self.put(Path(source).read_bytes(), suffix)


artifacts = ArtifactStore()
