import os
import json
import time
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.hash import bcrypt_sha256
import streamlit as st

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# Check if DATABASE_URL is available
if not DATABASE_URL:
    print("WARNING: DATABASE_URL environment variable not found!")
    print("Using SQLite database for testing purposes")
    DATABASE_URL = "sqlite:///./test.db"

# Only print the first part of the URL (before password info if present)
if '@' in DATABASE_URL:
    print(f"Using database connection: {DATABASE_URL.split('@')[0].split(':')[0]}...")

# Create engine and session with connection pool settings for better reliability
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    connect_args={"connect_timeout": 15} if "postgresql" in DATABASE_URL else {}  # Connection timeout only for PostgreSQL
)
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

# Add predefined users (will only add if they don't exist)
def create_predefined_users():
    db = SessionLocal()
    
    # Check if user1 exists
    user1 = db.query(User).filter(User.username == "info@civis.vote").first()
    if not user1:
        # Create user1
        user1 = User(
            username="info@civis.vote",
            email="info@civis.vote",
            hashed_password=User.get_password_hash("policy123"),
            is_active=True
        )
        db.add(user1)
    
    # Check if user2 exists
    user2 = db.query(User).filter(User.username == "jpmteam@civis.vote").first()
    if not user2:
        # Create user2
        user2 = User(
            username="jpmteam@civis.vote",
            email="jpmteam@civis.vote",
            hashed_password=User.get_password_hash("jpm@123"),
            is_active=True
        )
        db.add(user2)
    
    db.commit()
    db.close()

# Initialize predefined users
create_predefined_users()

# Database utility functions
def get_db():
    """Get a database session with better error handling"""
    db = None
    retry_attempts = 3
    retry_delay = 0.5  # seconds
    
    for attempt in range(retry_attempts):
        try:
            db = SessionLocal()
            # Test the connection with a simple query
            db.execute(text("SELECT 1"))
            return db
        except Exception as e:
            if db:
                db.close()
            
            if attempt < retry_attempts - 1:
                # Log the error and retry
                print(f"Database connection attempt {attempt+1} failed: {str(e)}")
                time.sleep(retry_delay)
            else:
                # Last attempt failed, raise the exception
                print(f"All database connection attempts failed: {str(e)}")
                raise

# We're not using this function anymore since registration is disabled
def register_user(username, email, password):
    """Register a new user in the database"""
    return False, "Registration is disabled"

def authenticate_user(username, password):
    """Authenticate a user with username and password"""
    try:
        db = get_db()
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False, "Invalid username or password"
        
        if not User.verify_password(password, user.hashed_password):
            return False, "Invalid username or password"
        
        return True, user
    except Exception as e:
        # Handle database connection errors gracefully
        print(f"Database authentication error: {str(e)}")
        return False, "Database connection error. Please try again."
    finally:
        # Ensure db is always closed
        if 'db' in locals():
            db.close()

def save_assessment(user_id, document_name, policy_summary, assessment_results, recommendations):
    """Save assessment results to history"""
    try:
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
        return assessment.id
    except Exception as e:
        print(f"Database error in save_assessment: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return None
    finally:
        if 'db' in locals():
            db.close()

def get_user_assessments(user_id):
    """Get all assessments for a specific user"""
    try:
        db = get_db()
        assessments = db.query(AssessmentHistory).filter(
            AssessmentHistory.user_id == user_id
        ).order_by(AssessmentHistory.created_at.desc()).all()
        
        # Copy the results to a list to avoid SQLAlchemy lazy loading issues
        result = []
        for assessment in assessments:
            result.append(assessment)
        
        return result
    except Exception as e:
        print(f"Database error in get_user_assessments: {str(e)}")
        return []
    finally:
        if 'db' in locals():
            db.close()

def get_assessment(assessment_id):
    """Get a specific assessment by ID"""
    try:
        db = get_db()
        assessment = db.query(AssessmentHistory).filter(
            AssessmentHistory.id == assessment_id
        ).first()
        return assessment
    except Exception as e:
        print(f"Database error in get_assessment: {str(e)}")
        return None
    finally:
        if 'db' in locals():
            db.close()

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
    if 'writing_findings' in st.session_state:
        st.session_state.writing_findings = []