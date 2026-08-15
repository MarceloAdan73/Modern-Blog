from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from database import engine, get_db, SessionLocal
from models.models import Base, User, Post
from models.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    PostCreate,
    PostResponse,
    UserUpdate,
)
from security import (
    create_access_token,
    get_current_user,
    set_current_request,
    reset_current_request,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func, text

# GraphQL imports
from strawberry.fastapi import GraphQLRouter
from graphql_schema import schema, get_graphql_context

# Create tables
Base.metadata.create_all(bind=engine)


def seed_demo_user():
    """Crea el usuario demo user/123456 si no existe y asigna los posts
    huerfanos (author_id NULL, creados antes de la auth real) a ese usuario.
    Asi el flujo demo funciona igual en local (SQLite) y en produccion."""
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.username == "user").first()
        if not demo_user:
            demo_user = User(
                username="user",
                email="user@example.com",
                full_name="John Doe (Demo User)",
                hashed_password=generate_password_hash("123456"),
            )
            db.add(demo_user)
            db.flush()

        # Migracion: posts legacy sin dueno -> usuario demo
        db.query(Post).filter(Post.author_id.is_(None)).update(
            {
                Post.author_id: demo_user.id,
                Post.author_name: demo_user.full_name or demo_user.username,
            }
        )
        db.commit()
    finally:
        db.close()


seed_demo_user()

app = FastAPI(title="Modern Blog", version="1.0")


@app.middleware("http")
async def capture_current_request(request, call_next):
    """Guarda la request en una contextvar (la usa el context de GraphQL)."""
    token = set_current_request(request)
    try:
        return await call_next(request)
    finally:
        reset_current_request(token)


# GraphQL router con GraphiQL (context con auth para las mutations)
graphql_app = GraphQLRouter(schema, graphql_ide="graphiql", context_getter=get_graphql_context)
app.include_router(graphql_app, prefix="/graphql")

# CORS restringido: solo la demo de Render (same-origin en local).
# Sin credentials: la auth es via header Authorization Bearer, no cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://modern-blog-tkzl.onrender.com",
        "http://localhost:10000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they do not exist
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== FRONTEND ====================
@app.get("/")
async def read_index():
    return FileResponse("templates/index.html")


# ==================== HEALTH CHECK ====================
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return {
        "success": db_status == "connected",
        "status": "healthy" if db_status == "connected" else "degraded",
        "message": "Modern Blog API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production" if os.environ.get("RENDER") else "development",
        "version": app.version,
        "database": db_status,
    }


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
        "access_token": create_access_token(db_user.id),
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
def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
    db_user = current_user

    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "profile_picture": db_user.profile_picture,
        "bio": db_user.bio,
        "location": db_user.location,
        "website": db_user.website,
        "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
    }


@app.put("/api/auth/profile", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.id == current_user.id).first()
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
def delete_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.id == current_user.id).first()
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

    # Mark as NOT owned (public listing; ownership requires auth)
    for post in posts:
        post.is_owner = False

    return posts


@app.post("/api/posts", response_model=PostResponse)
def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_post = Post(
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        author_id=current_user.id,
        author_name=current_user.full_name or current_user.username,
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    db_post.is_owner = True
    return db_post


@app.get("/api/posts/my-posts", response_model=List[PostResponse])
def get_my_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    posts = (
        db.query(Post)
        .filter(Post.author_id == current_user.id)
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

    # Mark as NOT owned (ownership requires auth)
    post.is_owner = False

    return post


@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You can only edit your own posts"
        )

    db_post.title = post.title
    db_post.content = post.content
    db_post.excerpt = post.excerpt
    db_post.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_post)
    db_post.is_owner = True
    return db_post


@app.delete("/api/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own posts"
        )

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
