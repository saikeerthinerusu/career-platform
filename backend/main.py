from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
import os
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import IntegrityError
from auth import hash_password, verify_password, create_access_token
from security import get_current_user
from models import User
import models
from database import Base, engine, get_db
from pydantic import BaseModel, Field
from models import StudentProfile, StudentSkill
from models import Career, CareerSkill, StudentSkill
from career_engine import rank_careers
from skillbridge.graph.knowledge_graph import build_graph
from datetime import datetime
from models import RoadmapStep, RoadmapProgress, StudentFeedback
from agent_v1 import generate_career_advice
from agent_v2 import calculate_reward
from models import AgentReward
from agent_v2 import update_linucb_reward
from models import Project

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Career Recommendation Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Career Platform API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "database": "connected",
    }
@app.get("/api/skillbridge/graph")
def skillbridge_graph():
    try:
        graph = build_graph()

        return {
            "message": "SkillBridge graph loaded successfully",
            "nodes": graph.nodes,
            "edges": graph.edges,
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


@app.post("/auth/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = User(
        username=data.username.strip(),
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already registered",
        )

    return {
        "message": "Registration successful",
        "user_id": user.id,
        "username": user.username,
    }


@app.post("/auth/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == form.username.strip())
        .first()
    )

    if user is None or not verify_password(
        form.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@app.get("/auth/me")
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }
class ProfileRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    college: str = Field(min_length=1, max_length=150)
    year_of_study: int = Field(ge=1, le=6)
    target_role: str = Field(min_length=1, max_length=100)
    interests: str = ""
    weekly_availability: int = Field(default=5, ge=0, le=100)
class ProgressRequest(BaseModel):
    completed: bool


class FeedbackRequest(BaseModel):
    career_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1000)


class RoadmapStepRequest(BaseModel):
    career_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    order_number: int = Field(default=1, ge=1)
    prerequisite_step_id: int | None = None

@app.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == current_user.id)
        .first()
    )

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "full_name": profile.full_name,
        "college": profile.college,
        "year_of_study": profile.year_of_study,
        "target_role": profile.target_role,
        "interests": profile.interests,
        "weekly_availability": profile.weekly_availability,
    }


@app.put("/profile")
def save_profile(
    data: ProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == current_user.id)
        .first()
    )

    if profile is None:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    profile.full_name = data.full_name
    profile.college = data.college
    profile.year_of_study = data.year_of_study
    profile.target_role = data.target_role
    profile.interests = data.interests
    profile.weekly_availability = data.weekly_availability

    db.commit()
    db.refresh(profile)

    return {
        "message": "Profile saved successfully",
        "full_name": profile.full_name,
    }
class SkillRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    proficiency: int = Field(ge=1, le=5)
    verification_status: str = "self-rated"


@app.get("/skills")
def get_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skills = (
        db.query(StudentSkill)
        .filter(StudentSkill.user_id == current_user.id)
        .all()
    )

    return [
        {
            "id": skill.id,
            "name": skill.name,
            "proficiency": skill.proficiency,
            "verification_status": skill.verification_status,
        }
        for skill in skills
    ]


@app.post("/skills", status_code=201)
def add_skill(
    data: SkillRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill = StudentSkill(
        user_id=current_user.id,
        name=data.name.strip(),
        proficiency=data.proficiency,
        verification_status=data.verification_status,
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return {
        "message": "Skill added successfully",
        "id": skill.id,
        "name": skill.name,
        "proficiency": skill.proficiency,
        "verification_status": skill.verification_status,
    }


@app.delete("/skills/{skill_id}")
def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.id == skill_id,
            StudentSkill.user_id == current_user.id,
        )
        .first()
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    db.delete(skill)
    db.commit()

    return {"message": "Skill deleted successfully"}

@app.get("/career-recommendations")
def get_career_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    student_records = (
        db.query(StudentSkill)
        .filter(StudentSkill.user_id == current_user.id)
        .all()
    )

    student_skills = {
        item.name.strip().lower(): item.proficiency
        for item in student_records
    }

    careers = db.query(Career).all()
    career_data = []

    for career in careers:
        required = {}

        for item in career.required_skills:
            required[item.skill_name] = item.importance

    career_data.append({
                "id": career.id,
                "career_id": career.id,
                "title": career.title,
                "description": career.description or "",
                "required_skills": required,
            })

    recommendations = rank_careers(student_skills, career_data)

    agent_advice = generate_career_advice(
        student_skills,
        recommendations,
    )

    return {
        "student_id": current_user.id,
        "recommendations": recommendations,
        "agent_advice": agent_advice,
    }

@app.get("/roadmap/{career_id}")
def get_roadmap(
    career_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    career = db.query(Career).filter(Career.id == career_id).first()

    if career is None:
        raise HTTPException(status_code=404, detail="Career not found")

    steps = (
        db.query(RoadmapStep)
        .filter(RoadmapStep.career_id == career_id)
        .order_by(RoadmapStep.order_number)
        .all()
    )

    progress_records = (
        db.query(RoadmapProgress)
        .filter(RoadmapProgress.user_id == current_user.id)
        .all()
    )

    progress_map = {item.step_id: item for item in progress_records}

    return {
        "career_id": career_id,
        "career": career.title,
        "roadmap": [
            {
                "step_id": step.id,
                "title": step.title,
                "description": step.description,
                "order_number": step.order_number,
                "prerequisite_step_id": step.prerequisite_step_id,
                "completed": (
                    progress_map[step.id].completed
                    if step.id in progress_map else False
                ),
            }
            for step in steps
        ],
    }

@app.put("/roadmap/progress/{step_id}")
def update_roadmap_progress(
    step_id: int,
    data: ProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    step = db.query(RoadmapStep).filter(
        RoadmapStep.id == step_id
    ).first()

    if step is None:
        raise HTTPException(
            status_code=404,
            detail="Roadmap step not found"
        )

    progress = db.query(RoadmapProgress).filter(
        RoadmapProgress.user_id == current_user.id,
        RoadmapProgress.step_id == step_id,
    ).first()

    if progress is None:
        progress = RoadmapProgress(
            user_id=current_user.id,
            step_id=step_id,
        )
        db.add(progress)

    progress.completed = data.completed
    progress.completed_at = (
        datetime.utcnow() if data.completed else None
    )

    db.commit()
    db.refresh(progress)

    return {
        "message": "Progress updated successfully",
        "step_id": step_id,
        "completed": progress.completed,
        "completed_at": progress.completed_at,
    }


@app.post("/feedback")
def submit_feedback(
    data: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    career = db.query(Career).filter(
        Career.id == data.career_id
    ).first()

    if career is None:
        raise HTTPException(
            status_code=404,
            detail="Career not found"
        )

    # Save the student's feedback
    feedback = StudentFeedback(
        user_id=current_user.id,
        career_id=data.career_id,
        rating=data.rating,
        comment=data.comment,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # Calculate roadmap progress for this career
    total_steps = db.query(RoadmapStep).filter(
        RoadmapStep.career_id == career.id
    ).count()

    completed_steps = (
        db.query(RoadmapProgress)
        .join(
            RoadmapStep,
            RoadmapProgress.step_id == RoadmapStep.id
        )
        .filter(
            RoadmapProgress.user_id == current_user.id,
            RoadmapStep.career_id == career.id,
            RoadmapProgress.completed == True
        )
        .count()
    )

    # Calculate reward using feedback and roadmap progress
    reward = calculate_reward(
        rating=data.rating,
        completed_steps=completed_steps,
        total_steps=total_steps,
    )
    reward_record = AgentReward(
    user_id=current_user.id,
    career_id=career.id,
    feedback_id=feedback.id,
    reward=reward,
    )
    db.add(reward_record)
    db.commit()
    update_linucb_reward(career.id, reward)
    
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": feedback.id,
        "career_id": feedback.career_id,
        "rating": feedback.rating,
        "completed_steps": completed_steps,
        "total_steps": total_steps,
        "reward": reward,
    }


@app.get("/feedback")
def get_my_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    feedbacks = (
        db.query(StudentFeedback)
        .filter(StudentFeedback.user_id == current_user.id)
        .order_by(StudentFeedback.created_at.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "career_id": item.career_id,
            "rating": item.rating,
            "comment": item.comment,
            "created_at": item.created_at,
        }
        for item in feedbacks
    ]

@app.get("/agent/reward-history")
def get_agent_reward_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rewards = (
        db.query(AgentReward)
        .filter(AgentReward.user_id == current_user.id)
        .order_by(AgentReward.created_at.desc())
        .all()
    )

    return {
        "user_id": current_user.id,
        "total_rewards": len(rewards),
        "reward_history": [
            {
                "career_id": item.career_id,
                "feedback_id": item.feedback_id,
                "reward": item.reward,
                "created_at": item.created_at,
            }
            for item in rewards
        ],
    }

@app.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Student profile
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id
    ).first()

    # 2. Student skills
    student_records = db.query(StudentSkill).filter(
        StudentSkill.user_id == current_user.id
    ).all()

    student_skills = {
        item.name.strip().lower(): item.proficiency
        for item in student_records
    }

    # 3. Career recommendations
    careers = db.query(Career).all()
    career_data = []

    
    for career in careers:
        required = {}

        for item in career.required_skills:
            required[item.skill_name] = item.importance

        career_data.append({
            "id": career.id,
            "career_id": career.id,
            "title": career.title,
            "description": career.description or "",
            "required_skills": required,
        })


    recommendations = rank_careers(student_skills, career_data)

    # 4. Roadmap progress for this student
    total_steps = db.query(RoadmapStep).count()

    completed_steps = db.query(RoadmapProgress).filter(
        RoadmapProgress.user_id == current_user.id,
        RoadmapProgress.completed.is_(True),
    ).count()

    progress_percentage = (
        round(completed_steps / total_steps * 100)
        if total_steps > 0 else 0
    )

    # 5. Feedback count
    total_feedback = db.query(StudentFeedback).filter(
        StudentFeedback.user_id == current_user.id
    ).count()

    # 6. Skill gap summary for the top recommendation
    skill_gap = {
        "strong_skills": [],
        "partial_skills": [],
        "missing_skills": [],
    }

    if recommendations:
        top_career = recommendations[0]

        skill_gap = {
            "strong_skills": top_career.get("strong_skills", []),
            "partial_skills": top_career.get("partial_skills", []),
            "missing_skills": top_career.get("missing_skills", []),
        }

    return {
        "student": {
            "id": current_user.id,
            "username": current_user.username,
            "profile": {
                            "full_name": profile.full_name if profile else None,
                            "college": profile.college if profile else None,
                            "year_of_study": profile.year_of_study if profile else None,
                            "target_role": profile.target_role if profile else None,
                            "interests": profile.interests if profile else None,
                            "weekly_availability": profile.weekly_availability if profile else None,
                        },
                    },
        "statistics": {
            "total_skills": len(student_records),
            "completed_roadmap_steps": completed_steps,
            "total_roadmap_steps": total_steps,
            "roadmap_progress_percentage": progress_percentage,
            "total_feedback": total_feedback,
        },
        "top_recommendation": recommendations[0] if recommendations else None,
        "all_recommendations": recommendations,
        "skill_gap": skill_gap,
    }

class ProjectRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    technologies: str = ""
    skills: str = ""


@app.get("/projects")
def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )

    return [
        {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "technologies": project.technologies,
            "skills": project.skills,
        }
        for project in projects
    ]


@app.post("/projects", status_code=201)
def create_project(
    data: ProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = Project(
        user_id=current_user.id,
        title=data.title.strip(),
        description=data.description,
        technologies=data.technologies,
        skills=data.skills,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return {
        "message": "Project created successfully",
        "id": project.id,
        "title": project.title,
    }


@app.put("/projects/{project_id}")
def update_project(
    project_id: int,
    data: ProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    project.title = data.title.strip()
    project.description = data.description
    project.technologies = data.technologies
    project.skills = data.skills

    db.commit()
    db.refresh(project)

    return {"message": "Project updated successfully"}


@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}
