from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import uuid
from score_final import extract_all_scores
from schedule import parse_all_panel_tables
from score import parse_scores
from profile import parse_student_profile

# -----------------------------
# Configuration
# -----------------------------
LOGIN_URL = "https://hemis.edu.af/student/login"
FINAL_SCORES_URL = "https://hemis.edu.af/student/final-scores-list"
SCORE_URL = "https://hemis.edu.af/student/scores-list"
SCHEDULE_URL = "https://hemis.edu.af/student/timetable/course"
PROFILE_URL = "https://hemis.edu.af/student/profile"
from fastapi.middleware.cors import CORSMiddleware


# -----------------------------
# FastAPI app
# -----------------------------

app = FastAPI(title="HEMIS Student Portal API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------------
# In-memory session store
# -----------------------------
active_sessions = {}  # token -> requests.Session()

# -----------------------------
# Request models
# -----------------------------
class UserLogin(BaseModel):
    email: str
    password: str

# -----------------------------
# Helper functions
# -----------------------------
def create_session():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session

def login_to_hemis(session, email: str, password: str):
    login_page = session.get(LOGIN_URL)
    login_page.raise_for_status()
    soup = BeautifulSoup(login_page.text, "html.parser")
    token_input = soup.find("input", {"name": "_token"})
    if not token_input:
        raise HTTPException(status_code=500, detail="CSRF token not found")

    csrf_token = token_input["value"]
    payload = {
        "_token": csrf_token,
        "form": "login",
        "guard": "student",
        "email": email,
        "password": password,
        "remember": "on"
    }
    response = session.post(LOGIN_URL, data=payload, allow_redirects=True)
    if "login" in response.url.lower():
        raise HTTPException(status_code=401, detail="Login failed")
    return session

def fetch_page(session, url: str):
    response = session.get(url)
    if "login" in response.url.lower():
        raise HTTPException(status_code=403, detail="Session expired or unauthorized")
    return response.text

def get_session(token: str):
    if token not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return active_sessions[token]

# -----------------------------
# Routes
# -----------------------------
@app.post("/login")
def login(user: UserLogin):
    session = create_session()
    login_to_hemis(session, user.email, user.password)
    # Generate token for this session
    token = str(uuid.uuid4())
    active_sessions[token] = session
    return {"token": token, "message": "Login successful"}

@app.get("/final-score")
def final_score(token: str = Header(...)):
    session = get_session(token)
    html = fetch_page(session, FINAL_SCORES_URL)
    return extract_all_scores(html)

@app.get("/score")
def score(token: str = Header(...)):
    session = get_session(token)
    html = fetch_page(session, SCORE_URL)
    return parse_scores(html)

@app.get("/schedule")
def schedule(token: str = Header(...)):
    session = get_session(token)
    html = fetch_page(session, SCHEDULE_URL)
    return parse_all_panel_tables(html)

@app.get("/profile")
def profile(token: str = Header(...)):
    session = get_session(token)
    html = fetch_page(session, PROFILE_URL)
    return parse_student_profile(html)

@app.post("/logout")
def logout(token: str = Header(...)):
    session = get_session(token)
    session.close()
    del active_sessions[token]
    return {"message": "Logged out successfully"}

