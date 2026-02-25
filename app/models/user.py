from sqlalchemy import Column, Boolean, String, Integer, text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )

    posts = relationship("Post", back_populates="author", passive_deletes=True)
