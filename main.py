from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from database import engine, SessionLocal
from models.models import Base, User, Post
from models.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    PostCreate,
    PostResponse,
    UserUpdate,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func

# GraphQL imports
from strawberry.fastapi import GraphQLRouter
from graphql_schema import schema

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Modern Blog", version="1.0")

# GraphQL router con GraphiQL
graphql_app = GraphQLRouter(schema, graphql_ide="graphiql")
app.include_router(graphql_app, prefix="/graphql")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they do not exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== FRONTEND ====================
@app.get("/")
async def read_index():
    return FileResponse("templates/index.html")


# ==================== AUTH ENDPOINTS ====================
@app.post("/api/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_password = generate_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not check_password_hash(db_user.hashed_password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": "mock-token",
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "profile_picture": db_user.profile_picture,
            "bio": db_user.bio,
            "location": db_user.location,
            "website": db_user.website,
            "created_at": db_user.created_at.isoformat()
            if db_user.created_at
            else None,
        },
    }


@app.get("/api/auth/me")
def get_current_user(db: Session = Depends(get_db)):
    # In real app use JWT, here we use first user
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "profile_picture": user.profile_picture,
        "bio": user.bio,
        "location": user.location,
        "website": user.website,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@app.put("/api/auth/profile", response_model=UserResponse)
def update_profile(user_update: UserUpdate, db: Session = Depends(get_db)):
    # In real app use JWT, here we use first user
    db_user = db.query(User).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.profile_picture is not None:
        db_user.profile_picture = user_update.profile_picture
    if user_update.bio is not None:
        db_user.bio = user_update.bio
    if user_update.location is not None:
        db_user.location = user_update.location
    if user_update.website is not None:
        db_user.website = user_update.website

    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/api/auth/profile")
def delete_profile(db: Session = Depends(get_db)):
    # In real app use JWT, here we use first user
    db_user = db.query(User).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user posts
    db.query(Post).filter(Post.author_id == db_user.id).delete()

    # Delete user
    db.delete(db_user)
    db.commit()

    return {"message": "User and all posts deleted successfully"}


# ==================== POSTS ENDPOINTS ====================
@app.get("/api/posts", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).all()

    # Add info if it's from current user (mock)
    # TEMPORARY FIX: Mark all as NOT owner until proper auth is implemented
    for post in posts:
        post.is_owner = False  # Temporary fix for security

    return posts


@app.post("/api/posts", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    # In real app use JWT, here we use first user
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_post = Post(
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        author_id=user.id,
        author_name=user.full_name or user.username,
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/api/posts/my-posts", response_model=List[PostResponse])
def get_my_posts(db: Session = Depends(get_db)):
    # In real app filter by authenticated user
    user = db.query(User).first()
    if not user:
        return []

    posts = (
        db.query(Post)
        .filter(Post.author_id == user.id)
        .order_by(Post.created_at.desc())
        .all()
    )

    # Mark as owned (this should remain True for user's own posts)
    for post in posts:
        post.is_owner = True

    return posts


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Mark as NOT owned (temporary security fix)
    post.is_owner = False

    return post


@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_post.title = post.title
    db_post.content = post.content
    db_post.excerpt = post.excerpt
    db_post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_post)
    return db_post


@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}


# ==================== DASHBOARD & STATS ====================
@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_posts = db.query(Post).count()

    # Most active user
    most_active = (
        db.query(User, func.count(Post.id).label("post_count"))
        .outerjoin(Post)
        .group_by(User.id)
        .order_by(func.count(Post.id).desc())
        .first()
    )

    most_active_user = most_active[0].username if most_active else "No users"

    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "most_active_user": most_active_user,
    }


@app.get("/api/users/{user_id}/stats")
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    user_posts = db.query(Post).filter(Post.author_id == user_id).all()
    total_posts = len(user_posts)
    total_words = sum(len(post.content.split()) for post in user_posts)
    average_words = total_words // total_posts if total_posts > 0 else 0
    last_post = (
        max(user_posts, key=lambda x: x.created_at).created_at if user_posts else None
    )

    return {
        "total_posts": total_posts,
        "total_words": total_words,
        "average_words_per_post": average_words,
        "last_post_date": last_post.isoformat() if last_post else None,
    }


if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, access_log=False)
