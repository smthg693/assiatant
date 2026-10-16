"""SQLAlchemy models for all Debug Dojo tables."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Learner profiles
# ---------------------------------------------------------------------------
class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    supabase_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    submissions: Mapped[list["Submission"]] = relationship(back_populates="learner", lazy="selectin")
    mistake_records: Mapped[list["MistakeRecord"]] = relationship(back_populates="learner", lazy="selectin")
    hint_usages: Mapped[list["HintUsage"]] = relationship(back_populates="learner", lazy="selectin")
    concept_masteries: Mapped[list["ConceptMastery"]] = relationship(back_populates="learner", lazy="selectin")


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------
class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)  # easy, medium, hard
    concepts: Mapped[str] = mapped_column(Text, nullable=False)  # comma-separated concept tags
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    tests: Mapped[list["ChallengeTest"]] = relationship(back_populates="challenge", lazy="selectin")


class ChallengeTest(Base):
    __tablename__ = "challenge_tests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id"), nullable=False, index=True)
    test_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    function_name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_args: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-encoded arguments
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-encoded expected value

    challenge: Mapped["Challenge"] = relationship(back_populates="tests")

    __table_args__ = (
        UniqueConstraint("challenge_id", "test_number", name="uq_challenge_test_number"),
    )


# ---------------------------------------------------------------------------
# Submissions
# ---------------------------------------------------------------------------
class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learner_profiles.id"), nullable=False, index=True)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    overall_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, passed, failed
    explanation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    learner: Mapped["LearnerProfile"] = relationship(back_populates="submissions")
    challenge: Mapped["Challenge"] = relationship()
    results: Mapped[list["SubmissionResult"]] = relationship(back_populates="submission", lazy="selectin")
    hint_usages: Mapped[list["HintUsage"]] = relationship(back_populates="submission", lazy="selectin")


class SubmissionResult(Base):
    __tablename__ = "submission_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("submissions.id"), nullable=False, index=True)
    test_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenge_tests.id"), nullable=False)
    test_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    outcome: Mapped[str] = mapped_column(String(20), nullable=False)  # passed, wrong_output, runtime_error, timeout
    actual_output: Mapped[str] = mapped_column(Text, default="")  # stored only server-side, never exposed for hidden
    stderr_output: Mapped[str] = mapped_column(Text, default="")

    submission: Mapped["Submission"] = relationship(back_populates="results")


# ---------------------------------------------------------------------------
# Mistake tracking
# ---------------------------------------------------------------------------
class MistakeRecord(Base):
    __tablename__ = "mistake_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learner_profiles.id"), nullable=False, index=True)
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("submissions.id"), nullable=False)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    learner: Mapped["LearnerProfile"] = relationship(back_populates="mistake_records")

    __table_args__ = (
        Index("ix_mistake_learner_category", "learner_id", "category"),
    )


# ---------------------------------------------------------------------------
# Hint usage
# ---------------------------------------------------------------------------
class HintUsage(Base):
    __tablename__ = "hint_usages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learner_profiles.id"), nullable=False, index=True)
    submission_id: Mapped[str] = mapped_column(String(36), ForeignKey("submissions.id"), nullable=False, index=True)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id"), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3, ...
    hint_text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(20), default="curated")  # curated, groq, fallback
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    learner: Mapped["LearnerProfile"] = relationship(back_populates="hint_usages")
    submission: Mapped["Submission"] = relationship(back_populates="hint_usages")


# ---------------------------------------------------------------------------
# Concept mastery
# ---------------------------------------------------------------------------
class ConceptMastery(Base):
    __tablename__ = "concept_masteries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learner_profiles.id"), nullable=False, index=True)
    concept: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 to 1.0
    total_challenges: Mapped[int] = mapped_column(Integer, default=0)
    completed_challenges: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    learner: Mapped["LearnerProfile"] = relationship(back_populates="concept_masteries")

    __table_args__ = (
        UniqueConstraint("learner_id", "concept", name="uq_learner_concept"),
    )


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------
class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learner_profiles.id"), nullable=False, index=True)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
