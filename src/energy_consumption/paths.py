from pathlib import Path


def find_project_root() -> Path:
    current = Path(__file__).resolve().parent

    for path in [current, *current.parents]:
        if (path / "pyproject.toml").exists():
            return path

    raise FileNotFoundError("루트를 찾을 수 없습니다")


PROJECT_ROOT = find_project_root()
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / 'model'