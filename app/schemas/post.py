from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, model_validator


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    is_public: bool = Field(default=True)


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)
    is_public: bool | None = None

    @model_validator(mode="after")
    def check_not_all_none(self):
        if self.title is None and self.content is None and self.is_public is None:
            raise ValueError("title and content cannot be both None")
        return self


class PostRead(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PostListResponse(BaseModel):
    items: list[PostRead]
    total: int
    skip: int
    limit: int
