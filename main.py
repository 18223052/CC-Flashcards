from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import create_engine, Session, SQLModel 
from typing import Annotated
from model import MOTD, MOTDBase
import secrets
import base64
import pyotp
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

templates = Jinja2Templates(directory="templates")
#FastAPI
app = FastAPI(docs_url=None, redoc_url=None)
security = HTTPBasic()
app.mount("/static", StaticFiles(directory="static"), name="static")

# SQLite Database
sqlite_file_name = "motd.db"
sqlite_url = f"sqlite:////{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]

# Users - lengkapi dengan userid dan shared_secret yang sesuai
users = {
    "sister": "ii2210_sister_1234",
    "fathy": "ii2210_fathy_1234"
}


@app.get("/", response_class=FileResponse)
async def root():
    return FileResponse("index.html")

last_id = 0
@app.get("/motd")
async def get_motd(session: SessionDep, request: Request):
    global last_id
    motds = session.query(MOTD).order_by(MOTD.id).all()

    if not motds:
        return templates.TemplateResponse("motd.html", {
            "request": request,
            "motd": "No message available",
            "creator": "-",
            "created_at": "-"
        })

    # Cari index dari last_id
    current_index = next((i for i, m in enumerate(motds) if m.id == last_id), -1)
    next_index = (current_index + 1) % len(motds)

    selected = motds[next_index]
    last_id = selected.id

    return templates.TemplateResponse("motd.html", {
        "request": request,
        "motd": selected.motd,
        "creator": selected.creator,
        "created_at": selected.created_at
    })



@app.post("/motd")
async def post_motd(message: MOTDBase, session: SessionDep, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):

	current_password_bytes = credentials.password.encode("utf8")

	valid_username, valid_password = False, False

	try:

		if credentials.username in users:
			valid_username = True
			s = base64.b32encode(users.get(credentials.username).encode("utf-8")).decode("utf-8")
			totp = pyotp.TOTP(s=s,digest="SHA256",digits=8)
			valid_password = secrets.compare_digest(current_password_bytes,totp.now().encode("utf8"))

			if valid_password and valid_username:
				motd = MOTD(motd=message.motd, creator=credentials.username)
				session.add(motd)
				session.commit()
				session.refresh(motd)
				return {"message": "MOTD added successfully."}
			
			else:

				raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid userid or password.") 
			
		else:

			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid userid or password.")
		
	except HTTPException as e:

	    raise e
     

def seed_motd(session):
    existing = session.query(MOTD).first()
    if existing:
        return  # Data sudah ada, tidak perlu seed ulang

    quotes = [
        ("The only thing we have to fear is fear itself.", "Franklin D. Roosevelt"),
        ("The time is always right to do what is right.", "Martin Luther King Jr."),
        ("Be the change that you wish to see in the world.", "Mahatma Gandhi"),
        ("It always seems impossible until it's done.", "Nelson Mandela"),
        ("Stay hungry, stay foolish.", "Steve Jobs"),
        ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
        ("All our dreams can come true, if we have the courage to pursue them.", "Walt Disney"),
        ("The greatest glory in living lies not in never falling, but in rising every time we fall.", "Nelson Mandela"),
        ("The way to get started is to quit talking and begin doing.", "Walt Disney"),
        ("Believe you can and you're halfway there.", "Theodore Roosevelt")
    ]

    for quote, author in quotes:
        session.add(MOTD(motd=quote, creator=author))

    session.commit()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        seed_motd(session)

if __name__ == "__main__":
    import uvicorn
    create_db_and_tables()

    # seed data saat start pertama kali
    with Session(engine) as session:
        seed_motd(session)

    uvicorn.run("main:app", host="0.0.0.0", port=17787)
