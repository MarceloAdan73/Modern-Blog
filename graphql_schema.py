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

    @strawberry.field
    def authorName(self) -> str:
        return self.author_name

    @strawberry.field
    def createdAt(self) -> str:
        return self.created_at


@strawberry.type
class Query:
    @strawberry.field
    def posts(self) -> List[PostType]:
        db = SessionLocal()
        try:
            posts = db.query(Post).order_by(Post.created_at.desc()).all()
            return [
                PostType(
                    id=p.id,
                    title=p.title,
                    content=p.content,
                    excerpt=p.excerpt or "",
                    status=p.status or "Published",
                    tags=p.tags or "[]",
                    author_name=p.author_name,
                    created_at=p.created_at.strftime("%Y-%m-%d %H:%M")
                    if p.created_at
                    else "",
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


@strawberry.input
class PostUpdateInput:
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[str] = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_post(self, post_data: PostInput) -> PostType:
        db = SessionLocal()
        try:
            new_post = Post(
                title=post_data.title,
                content=post_data.content,
                excerpt=post_data.excerpt,
                status=post_data.status,
                tags=post_data.tags,
                author_name=post_data.author_name,
                created_at=datetime.now(),
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
                created_at=new_post.created_at.strftime("%Y-%m-%d %H:%M"),
            )
        finally:
            db.close()

    @strawberry.mutation
    def update_post(self, id: int, post_data: PostUpdateInput) -> Optional[PostType]:
        db = SessionLocal()
        try:
            db_post = db.query(Post).filter(Post.id == id).first()
            if not db_post:
                return None

            if post_data.title is not None:
                db_post.title = post_data.title
            if post_data.content is not None:
                db_post.content = post_data.content
            if post_data.excerpt is not None:
                db_post.excerpt = post_data.excerpt
            if post_data.status is not None:
                db_post.status = post_data.status
            if post_data.tags is not None:
                db_post.tags = post_data.tags

            db_post.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_post)

            return PostType(
                id=db_post.id,
                title=db_post.title,
                content=db_post.content,
                excerpt=db_post.excerpt or "",
                status=db_post.status or "Published",
                tags=db_post.tags or "[]",
                author_name=db_post.author_name,
                created_at=db_post.created_at.strftime("%Y-%m-%d %H:%M"),
            )
        finally:
            db.close()

    @strawberry.mutation
    def delete_post(self, id: int) -> bool:
        db = SessionLocal()
        try:
            db_post = db.query(Post).filter(Post.id == id).first()
            if not db_post:
                return False

            db.delete(db_post)
            db.commit()
            return True
        finally:
            db.close()


schema = strawberry.Schema(query=Query, mutation=Mutation)
