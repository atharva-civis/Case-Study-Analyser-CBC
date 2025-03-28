import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.hash import bcrypt_sha256
import streamlit as st

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to history records
    assessments = relationship("AssessmentHistory", back_populates="user")
    
    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return bcrypt_sha256.verify(plain_password, hashed_password)
    
    @classmethod
    def get_password_hash(cls, password):
        return bcrypt_sha256.hash(password)

# Define AssessmentHistory model
class AssessmentHistory(Base):
    __tablename__ = "assessment_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_name = Column(String)
    policy_summary = Column(Text)
    assessment_results = Column(Text)  # Store JSON data
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="assessments")
    
    def get_results_dict(self):
        """Convert the stored JSON string back to a dictionary"""
        if self.assessment_results:
            try:
                return json.loads(self.assessment_results)
            except:
                return {}
        return {}

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Database utility functions
def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def register_user(username, email, password):
    """Register a new user in the database"""
    db = get_db()
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        db.close()
        return False, "Username already exists"
    
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        db.close()
        return False, "Email already exists"
    
    # Create new user
    hashed_password = User.get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return True, "User registered successfully"

def authenticate_user(username, password):
    """Authenticate a user with username and password"""
    db = get_db()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        db.close()
        return False, "Invalid username or password"
    
    if not User.verify_password(password, user.hashed_password):
        db.close()
        return False, "Invalid username or password"
    
    db.close()
    return True, user

def save_assessment(user_id, document_name, policy_summary, assessment_results, recommendations):
    """Save assessment results to history"""
    db = get_db()
    
    # Convert assessment_results to JSON string
    assessment_results_json = json.dumps(assessment_results)
    
    # Create new assessment history record
    assessment = AssessmentHistory(
        user_id=user_id,
        document_name=document_name,
        policy_summary=policy_summary,
        assessment_results=assessment_results_json,
        recommendations=recommendations
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    db.close()
    return assessment.id

def get_user_assessments(user_id):
    """Get all assessments for a specific user"""
    db = get_db()
    assessments = db.query(AssessmentHistory).filter(
        AssessmentHistory.user_id == user_id
    ).order_by(AssessmentHistory.created_at.desc()).all()
    db.close()
    return assessments

def get_assessment(assessment_id):
    """Get a specific assessment by ID"""
    db = get_db()
    assessment = db.query(AssessmentHistory).filter(
        AssessmentHistory.id == assessment_id
    ).first()
    db.close()
    return assessment

# Streamlit session state utilities
def initialize_session_state():
    """Initialize session state variables for authentication"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None

def login_user(user):
    """Set session state for logged in user"""
    st.session_state.logged_in = True
    st.session_state.user_id = user.id
    st.session_state.username = user.username

def logout_user():
    """Clear session state for logout"""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    # Clear assessment related session state
    if 'policy_text' in st.session_state:
        st.session_state.policy_text = ""
    if 'policy_analysis' in st.session_state:
        st.session_state.policy_analysis = None
    if 'policy_summary' in st.session_state:
        st.session_state.policy_summary = ""
    if 'assessment_results' in st.session_state:
        st.session_state.assessment_results = {}
    if 'document_name' in st.session_state:
        st.session_state.document_name = ""
    if 'recommendations' in st.session_state:
        st.session_state.recommendations = ""