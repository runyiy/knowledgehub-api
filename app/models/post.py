from sqlalchemy import (
    Column,
    Boolean,
    String,
    Integer,
    ForeignKey,
    Text,
    text,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), index=True, nullable=False)
    content = Column(Text, nullable=False)
    is_public = Column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    summary = Column(String, nullable=True)

    author = relationship("User", back_populates="posts")
