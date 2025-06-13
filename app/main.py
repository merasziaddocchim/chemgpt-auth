from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app import models, schemas, database, utils
import uuid

app = FastAPI()

# Create tables (for dev only, not prod migrations! okay)
models.Base.metadata.create_all(bind=database.engine)

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified. You can now log in."}

@app.post("/register", response_model=schemas.UserRead)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = utils.hash_password(user.password)
    token = str(uuid.uuid4())  # Generate a unique verification token
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pw,
        verification_token=token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print("Verification token (mock):", db_user.verification_token)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not db_user.is_verified:
        raise HTTPException(status_code=401, detail="Email not verified")
    if not utils.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = utils.create_access_token({"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
