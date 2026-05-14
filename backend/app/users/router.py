import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.users import repository
from app.users.schemas import UserCreate, UserRead, UserUpdate


router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger("app.users")


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    request: Request,
    user_create: UserCreate,
    db: Session = Depends(get_db),
) -> UserRead:
    user = repository.create_user(db, user_create)
    logger.info(
        "[USERS CREATE SUCCESS] request_id=%s | user_id=%s | has_source_url=%s | tags_count=%s",
        request.state.request_id,
        user.id,
        user.source_url is not None,
        len(user.tags),
    )
    return user


@router.get("", response_model=list[UserRead])
def list_users(
    request: Request,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    users = repository.list_users(db, skip=skip, limit=limit)
    logger.info(
        "[USERS LIST SUCCESS] request_id=%s | skip=%s | limit=%s | returned=%s",
        request.state.request_id,
        skip,
        limit,
        len(users),
    )
    return users


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> UserRead:
    user = repository.get_user(db, user_id)
    if user is None:
        logger.warning(
            "[USERS READ NOT FOUND] request_id=%s | user_id=%s",
            request.state.request_id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    logger.info(
        "[USERS READ SUCCESS] request_id=%s | user_id=%s | has_source_url=%s",
        request.state.request_id,
        user.id,
        user.source_url is not None,
    )
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    request: Request,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
) -> UserRead:
    user = repository.get_user(db, user_id)
    if user is None:
        logger.warning(
            "[USERS UPDATE NOT FOUND] request_id=%s | user_id=%s",
            request.state.request_id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    updated_fields = (
        ",".join(user_update.model_dump(exclude_unset=True).keys())
        or "none"
    )
    updated_user = repository.update_user(db, user, user_update)
    logger.info(
        "[USERS UPDATE SUCCESS] request_id=%s | user_id=%s | updated_fields=%s",
        request.state.request_id,
        updated_user.id,
        updated_fields,
    )
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    user = repository.get_user(db, user_id)
    if user is None:
        logger.warning(
            "[USERS DELETE NOT FOUND] request_id=%s | user_id=%s",
            request.state.request_id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    repository.delete_user(db, user)
    logger.info(
        "[USERS DELETE SUCCESS] request_id=%s | user_id=%s",
        request.state.request_id,
        user_id,
    )
