from sqlmodel import SQLModel, Field

class Flashcard(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question: str
    answer: str
