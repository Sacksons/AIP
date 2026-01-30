"""Authentication router."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.config import settings
from app.models.user import User
from app.models.organization import OrgMember
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token."""
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == int(user_id)).first()
    return user


def require_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Require authenticated user."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    return current_user


def get_user_role(current_user: User, db: Session) -> str:
    """Get user's primary role from organization membership."""
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == "active"
    ).first()
    return membership.role if membership else "user"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/token", response_model=Token)
def login_for_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login."""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Get user role
    role = get_user_role(user, db)

    # Create token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": role,
        }
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60
    )


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Get user role
    role = get_user_role(user, db)

    # Create token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": role,
        }
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(require_auth)):
    """Get current authenticated user's information."""
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(require_auth)):
    """Logout current user (client should discard token)."""
    return {"message": "Successfully logged out"}
