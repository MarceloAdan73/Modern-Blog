import strawberry
from typing import List, Optional
from datetime import datetime
from graphql import GraphQLError
from database import SessionLocal
from models.models import Post, User
from security import decode_access_token, get_current_request


def _auth_user(request) -> Optional[User]:
    """Lee el Bearer token del header y devuelve el User (o None)."""
    if request is None:
        return None

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    user_id = decode_access_token(auth_header[7:])
    if user_id is None:
        return None

    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_graphql_context():
    """Contexto GraphQL: expone el usuario autenticado (si hay).

    IMPORTANTE: NO recibe argumentos (bug de strawberry 0.324: un
    context_getter con parametro request rompe la validacion del body).
    La request se lee de la contextvar capturada por el middleware.
    """
    request = get_current_request()
    return {"request": request, "user": _auth_user(request)}


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
    # Campo legacy del schema viejo: NO se usa (el autor sale del token
    # autenticado en create_post). Se mantiene opcional para no romper
    # clientes que ya lo envian (la UI lo manda) y para no exigirlo
    # a clientes nuevos.
    author_name: Optional[str] = None


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
    def create_post(self, post_data: PostInput, info: strawberry.Info) -> PostType:
        user = info.context["user"]
        if not user:
            raise GraphQLError("Not authenticated")

        db = SessionLocal()
        try:
            new_post = Post(
                title=post_data.title,
                content=post_data.content,
                excerpt=post_data.excerpt,
                status=post_data.status,
                tags=post_data.tags,
                author_id=user.id,
                author_name=user.full_name or user.username,
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
    def update_post(
        self, id: int, post_data: PostUpdateInput, info: strawberry.Info
    ) -> Optional[PostType]:
        user = info.context["user"]
        if not user:
            raise GraphQLError("Not authenticated")

        db = SessionLocal()
        try:
            db_post = db.query(Post).filter(Post.id == id).first()
            if not db_post:
                return None
            if db_post.author_id != user.id:
                raise GraphQLError("You can only edit your own posts")

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
    def delete_post(self, id: int, info: strawberry.Info) -> bool:
        user = info.context["user"]
        if not user:
            raise GraphQLError("Not authenticated")

        db = SessionLocal()
        try:
            db_post = db.query(Post).filter(Post.id == id).first()
            if not db_post:
                return False
            if db_post.author_id != user.id:
                raise GraphQLError("You can only delete your own posts")

            db.delete(db_post)
            db.commit()
            return True
        finally:
            db.close()


schema = strawberry.Schema(query=Query, mutation=Mutation)
