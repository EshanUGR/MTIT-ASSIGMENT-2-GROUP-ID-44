from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .. import models, schemas, auth_utils, database

router = APIRouter(prefix="/users", tags=["Users"])
security = HTTPBearer()


def get_current_payload(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return auth_utils.decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user(
    payload: dict = Depends(get_current_payload),
    db: Session = Depends(database.get_db),
):
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(payload: dict = Depends(get_current_payload)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload

@router.post("/", response_model=schemas.UserResponse)
def register_patient(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = auth_utils.hash_password(user.password)
    new_user = models.User(**user.model_dump(exclude={"password"}), password=hashed_pwd)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=List[schemas.UserResponse])
def get_all_patients(
    db: Session = Depends(database.get_db),
    _: dict = Depends(require_admin),
):
    return db.query(models.User).all()

@router.get("/me", response_model=schemas.UserResponse)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_patient(
    user_id: int,
    db: Session = Depends(database.get_db),
    _: dict = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_patient(user_id: int, updates: schemas.UserUpdate, db: Session = Depends(database.get_db)):
    user_query = db.query(models.User).filter(models.User.id == user_id)
    if not user_query.first():
        raise HTTPException(status_code=404, detail="User not found")
    
    user_query.update(updates.model_dump(exclude_unset=True))
    db.commit()
    return user_query.first()


@router.patch("/{user_id}/deactivate", response_model=schemas.UserResponse)
def deactivate_patient(
    user_id: int,
    db: Session = Depends(database.get_db),
    _: dict = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.status = "inactive"
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=schemas.DeleteResponse)
def delete_patient(
    user_id: int,
    db: Session = Depends(database.get_db),
    _: dict = Depends(require_admin),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted permanently", "id": user_id}


@router.post("/login", response_model=schemas.LoginResponse)
def login_patient(payload: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not auth_utils.verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    admin_emails = auth_utils.get_admin_emails()
    role = "admin" if user.email.lower() in admin_emails else "patient"

    access_token = auth_utils.create_access_token(
        {"sub": str(user.id), "email": user.email, "role": role}
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "role": role,
        "user": user,
    }

