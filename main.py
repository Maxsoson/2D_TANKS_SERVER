from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import sys
import ssl

# --- Логування ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addFilter(lambda record: 'ConnectionResetError' not in record.getMessage())

# --- База даних ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("❌ DATABASE_URL не встановлено в середовищі.")
    sys.exit(1)

try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        connect_args={"ssl": ssl.create_default_context()}
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    Base = declarative_base()
except Exception as e:
    logger.error(f"❌ Не вдалося створити engine: {e}")
    sys.exit(1)

# --- SQLAlchemy модель ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

# --- SMTP ---
SMTP_SERVER = "smtp.gmail.com"
PORT = 587
SENDER_EMAIL = "2dtankdiploma@gmail.com"
APP_PASSWORD = "nejgklwyqrtucdzf"

# --- FastAPI ---
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# --- Створення таблиць при запуску ---
@app.on_event("startup")
async def on_startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Таблиця 'users' успішно створена або вже існує.")
    except Exception as e:
        logger.error(f"❌ Помилка при створенні таблиць: {e}")
        sys.exit(1)

@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/index.html")

@app.get("/{page_name}", response_class=HTMLResponse)
async def serve_page(request: Request, page_name: str):
    return templates.TemplateResponse(page_name, {"request": request})

class UserRegister(BaseModel):
    name: str
    password: str

@app.post("/register")
async def register_user(request: Request, email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    async with async_session() as session:
        result = await session.execute(select(User).filter((User.email == email) | (User.name == name)))
        existing_user = result.scalars().first()

        if existing_user:
            if existing_user.email == email and existing_user.name == name:
                return JSONResponse({"message": "Користувач із такою електронною адресою та псевдонімом уже існує.", "status": "error"}, status_code=400)
            elif existing_user.email == email:
                return JSONResponse({"message": "Користувач із цією електронною адресою вже існує.", "status": "error"}, status_code=400)
            elif existing_user.name == name:
                return JSONResponse({"message": "Користувач із таким псевдонімом уже існує.", "status": "error"}, status_code=400)

        new_user = User(name=name, email=email, password=password)
        session.add(new_user)
        await session.commit()
        return JSONResponse({"message": "Користувач успішно зареєстрований", "status": "success"}, status_code=201)

@app.post("/login")
async def login_user(name: str = Form(...), password: str = Form(...)):
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.name == name, User.password == password))
        user = result.scalars().first()

        if user:
            return JSONResponse({
                "message": "Login successful",
                "name": user.name,
                "email": user.email
            })
        else:
            return JSONResponse({"message": "Invalid login or password"}, status_code=401)

@app.post("/recover-password")
async def recover_password(name: str = Form(...), email: str = Form(...)):
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.name == name, User.email == email))
        user = result.scalars().first()

        if not user:
            return JSONResponse({"message": "Користувача не знайдено."}, status_code=404)

        message = MIMEMultipart("alternative")
        message["From"] = SENDER_EMAIL
        message["To"] = email
        message["Subject"] = "Відновлення паролю"
        html = f"""<html><body><h1>Ваш пароль:</h1><p>{user.password}</p></body></html>"""
        message.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(SMTP_SERVER, PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.sendmail(SENDER_EMAIL, email, message.as_string())
            return JSONResponse({"message": "Пароль успішно надіслано."})
        except Exception as e:
            return JSONResponse({"message": f"Помилка надсилання: {str(e)}"}, status_code=500)

@app.post("/send-bug-report")
async def send_bug_report(name: str = Form(...), email: str = Form(...), subject: str = Form(...), msg: str = Form(...)):
    message = MIMEMultipart('alternative')
    message['From'] = SENDER_EMAIL
    message['To'] = SENDER_EMAIL
    message['Subject'] = f'Bug Report: {subject}'
    html = f"""<html><body><p>Від: {name} ({email})</p><p>Повідомлення: {msg}</p><p>Час: {now}</p></body></html>"""
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, SENDER_EMAIL, message.as_string())
        return {"message": "Bug report sent successfully"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)