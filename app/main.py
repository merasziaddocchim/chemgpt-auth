from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, schemas, database, utils
import uuid

app = FastAPI()

# Create tables (do this only for local dev or SQLite, not for prod migrations!)
models.Base.metadata.create_all(bind=database.engine)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
