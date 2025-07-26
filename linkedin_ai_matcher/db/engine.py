from pathlib import Path
from multiprocessing import Lock

from sqlalchemy import Engine, create_engine


engine: Engine | None = None
engine_lock = Lock()


def get_engine(db_path: Path = Path(".data/jobs.db")):
    global engine, engine_lock
    
    with engine_lock:
        if engine is None:
            engine = create_engine(f"sqlite:///{db_path}")
        return engine
