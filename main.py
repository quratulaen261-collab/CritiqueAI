from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from analyzer import analyze_website

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Users database (add more users here) ──
USERS = {
    "admin": "1234",
    "demo":  "demo",
    "user":  "password"
}

class LoginData(BaseModel):
    username: str
    password: str

class Website(BaseModel):
    url: str


@app.get("/")
def root():
    return {"status": "CritiqueAI backend is running"}


@app.post("/login")
def login(data: LoginData):
    if data.username in USERS and USERS[data.username] == data.password:
        return {"success": True, "username": data.username}
    return {"success": False, "message": "Invalid username or password"}


@app.post("/analyze")
def analyze(site: Website):
    result = analyze_website(site.url)
    return result
