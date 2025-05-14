from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select
from model import Flashcard

app = FastAPI()

# Setup database
engine = create_engine("sqlite:///flashcards.db")

# Templates & static
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load flashcard by index
@app.get("/", response_class=HTMLResponse)
async def read_flashcard(request: Request, index: int = 0):
    with Session(engine) as session:
        flashcards = session.exec(select(Flashcard)).all()
        if not flashcards:
            return templates.TemplateResponse("index.html",  {
                "request": request,
                "error": "No flashcards available",
            })

        if index >= len(flashcards):
            index = len(flashcards) - 1

        flashcard = flashcards[index]
        return templates.TemplateResponse("flashcard.html", {
            "request": request,
            "flashcard": flashcard,
            "index": index,
            "total": len(flashcards)
        })
