from pathlib import Path
from sqlalchemy import create_engine


def get_engine(db_path: Path = Path(".data/jobs.db")):
    return create_engine(f"sqlite:///{db_path}")
