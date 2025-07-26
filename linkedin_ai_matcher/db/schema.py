from abc import ABC

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase): ...


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, company={self.company})>"


class Match(Base):
    __tablename__ = "matches"

    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    fit: Mapped[str] = mapped_column(String, nullable=False)
    reasons: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        reasons_preview = "".join(filter(lambda s: not s.isspace(), self.reasons[:50]))
        return f"<Match(job_id={self.job_id}, fit={self.fit}, reasons={reasons_preview}...)>"
