import strawberry
from typing import List, Optional
from datetime import datetime
from database import SessionLocal
from models.models import Post

@strawberry.type
class PostType:
    id: int
    title: str
    content: str
    excerpt: Optional[str]
    status: str
    tags: str
    author_name: str
    created_at: str

@strawberry.type
class Query:
    @strawberry.field
    async def posts(self) -> List[PostType]:
        db = SessionLocal()
        try:
            posts = db.query(Post).all()
            return [
                PostType(
                    id=p.id,
                    title=p.title,
                    content=p.content,
                    excerpt=p.excerpt or "",
                    status=p.status or "Published",
                    tags=p.tags or "[]",
                    author_name=p.author_name,
                    created_at=p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else ""
                )
                for p in posts
            ]
        finally:
            db.close()

@strawberry.input
class PostInput:
    title: str
    content: str
    excerpt: Optional[str] = ""
    status: Optional[str] = "Published"
    tags: Optional[str] = "[]"
    author_name: str

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_post(self, post_data: PostInput) -> PostType:
        db = SessionLocal()
        try:
            new_post = Post(
                title=post_data.title,
                content=post_data.content,
                excerpt=post_data.excerpt,
                status=post_data.status,
                tags=post_data.tags,
                author_name=post_data.author_name,
                created_at=datetime.now()
            )
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            
            return PostType(
                id=new_post.id,
                title=new_post.title,
                content=new_post.content,
                excerpt=new_post.excerpt or "",
                status=new_post.status or "Published",
                tags=new_post.tags or "[]",
                author_name=new_post.author_name,
                created_at=new_post.created_at.strftime("%Y-%m-%d %H:%M")
            )
        finally:
            db.close()

schema = strawberry.Schema(query=Query, mutation=Mutation)
