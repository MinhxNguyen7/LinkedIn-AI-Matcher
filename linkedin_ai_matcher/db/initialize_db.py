from .schema import Base
from .engine import get_engine


def initialize_db():
    engine = get_engine()
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    initialize_db()
