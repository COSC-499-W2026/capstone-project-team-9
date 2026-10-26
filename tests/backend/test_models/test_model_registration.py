from pathlib import Path
from sqlmodel import SQLModel
import models  # (registers the table models)

EXPECTED_TABLES = {"language", "difficulty", "game", "target", "clue"}

def test_all_table_models_are_registered():
    assert EXPECTED_TABLES <= set(SQLModel.metadata.tables)

def test_every_model_file_is_imported_in_models_init():
    folder = Path(models.__file__).parent
    init_lines = (folder / "__init__.py").read_text().splitlines()
    init_text = "\n".join(l for l in init_lines if not l.lstrip().startswith("#")) # strip commented lines
    for path in folder.glob("*.py"):
        if path.stem != "__init__":
            assert f".{path.stem} import" in init_text, f"{path.name} not imported in __init__.py"