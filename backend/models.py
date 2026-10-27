from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    skills = relationship(
        "StudentSkill",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    full_name = Column(String(120), default="")
    college = Column(String(200), default="")
    year_of_study = Column(Integer, nullable=True)
    target_role = Column(String(120), default="")
    interests = Column(Text, default="")
    weekly_availability = Column(Integer, default=5)

    user = relationship("User", back_populates="profile")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    name = Column(String(100), nullable=False)
    proficiency = Column(Integer, default=1)
    verification_status = Column(String(20), default="self-rated")

    user = relationship("User", back_populates="skills")


class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), unique=True, nullable=False)
    description = Column(Text, default="")

    required_skills = relationship(
        "CareerSkill",
        back_populates="career",
        cascade="all, delete-orphan",
    )


class CareerSkill(Base):
    __tablename__ = "career_skills"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(
        Integer, ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=False
    )
    skill_name = Column(String(100), nullable=False)
    importance = Column(Float, default=1.0)

    career = relationship("Career", back_populates="required_skills")


class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"

    id = Column(Integer, primary_key=True, index=True)
    career_id = Column(
        Integer, ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    order_number = Column(Integer, default=1)
    prerequisite_step_id = Column(
        Integer, ForeignKey("roadmap_steps.id"), nullable=True
    )


class RoadmapProgress(Base):
    __tablename__ = "roadmap_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    step_id = Column(
        Integer, ForeignKey("roadmap_steps.id", ondelete="CASCADE"),
        nullable=False
    )
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)


class StudentFeedback(Base):
    __tablename__ = "student_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    career_id = Column(
        Integer, ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=False
    )
    rating = Column(Integer, nullable=False)
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    action_type = Column(String(80), nullable=False)
    context_json = Column(Text, default="{}")
    explanation = Column(Text, default="")
    policy_name = Column(String(40), default="rules")
    reward = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentReward(Base):
    __tablename__ = "agent_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    career_id = Column(
        Integer,
        ForeignKey("careers.id", ondelete="CASCADE"),
        nullable=False
    )
    feedback_id = Column(
        Integer,
        ForeignKey("student_feedback.id", ondelete="CASCADE"),
        nullable=False
    )
    reward = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
class Project(Base):
    __tablename__ = "student_projects"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    technologies = Column(Text, default="")
    skills = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )