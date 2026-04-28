from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta

from Backend.db import SessionLocal
from Backend.models import Users
from Backend.schemas import Login, Register

router = APIRouter()

SECRET_KEY = "sameerkhan197"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_DAYS = 7
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(email: str):
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": email,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
def register(data: Register, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == data.email).first()
    
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = Users(
        email=data.email,
        password=data.password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}

@router.post("/login")
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.email == data.email).first()
    
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user.email)
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/home")
def home(email: str = Depends(verify_token)):
    return {
        "message": f"Welcome {email} 🎉"
    }
