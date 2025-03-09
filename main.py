from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi_login import LoginManager

app = FastAPI()

# Підключення статичних файлів
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/CSS", StaticFiles(directory="static/CSS"), name="CSS")
app.mount("/JavaScript", StaticFiles(directory="static/JavaScript"), name="JavaScript")
app.mount("/Images", StaticFiles(directory="static/Images"), name="Images")

# Підключення шаблонів HTML
templates = Jinja2Templates(directory="templates")

# Налаштування SQLite
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Менеджер входу
SECRET_KEY = "your_secret_key"
login_manager = LoginManager(SECRET_KEY, token_url="/login")

@login_manager.user_loader
def load_user(email: str, db=Depends(get_db)):
    return db.query(User).filter(User.email == email).first()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register.html", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    user = User(username=username, email=email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        return {"error": "Невірний email або пароль"}
    access_token = login_manager.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/logout")
async def logout():
    return RedirectResponse(url="/")

# Інші сторінки
@app.get("/bug_report.html", response_class=HTMLResponse)
async def bug_report(request: Request):
    return templates.TemplateResponse("bug_report.html", {"request": request})

@app.get("/leaderboard.html", response_class=HTMLResponse)
async def leaderboard(request: Request):
    return templates.TemplateResponse("leaderboard.html", {"request": request})

# Налаштування SMTP
PORT = 2525
SMTP_SERVER = "smtp.mailmug.net"
LOGIN = "nfqxj2tsmptkmaui"
PASSWORD = "tekpt2sv3octwluf"
SENDER_EMAIL = "diplomatanki2025@gmail.com"
TO_EMAIL = "2dtankdiploma@gmail.com"

@app.post("/send-bug-report")
async def send_bug_report(name: str = Form(...), email: str = Form(...), subject: str = Form(...), msg: str = Form(...)):
    message = MIMEMultipart('alternative')
    message['From'] = SENDER_EMAIL
    message['To'] = TO_EMAIL
    message['Subject'] = f'Bug Report: {subject}'

    html = f"""
    <html>
    <body>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>Message:</strong> {msg}</p>
    </body>
    </html>
    """
    
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, PORT) as server:
            server.login(LOGIN, PASSWORD)
            server.sendmail(SENDER_EMAIL, TO_EMAIL, message.as_string())
        
        return {"msg": "Повідомлення успішно надіслано"}
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
