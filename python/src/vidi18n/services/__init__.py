from pathlib import Path
from typing import Iterator


def get_subpackages() -> Iterator[str]:
    me = __name__
    this_dir = Path(__file__).parent
    base_path = Path(this_dir)
    for child in base_path.iterdir():
        if child.is_dir() and (child / "__main__.py").exists():
            yield f"{me}.{child.name}.__main__"


ALL_PACKAGES = list(get_subpackages())
