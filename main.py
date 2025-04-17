# --- Імпорт нових бібліотек для PostgreSQL через SQLAlchemy ---
from fastapi import FastAPI, Request, Form, Depends
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


# --- Додано фільтр логів для винятку ConnectionResetError ---
class ConnectionResetFilter(logging.Filter):
    def filter(self, record):
        return 'ConnectionResetError' not in record.getMessage()

logging.getLogger("uvicorn.error").addFilter(ConnectionResetFilter())

# --- Замість SQLite використовується PostgreSQL через DATABASE_URL з оточення ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# --- SQLAlchemy модель таблиці users ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

# --- Налаштування SMTP (без змін) ---
SMTP_SERVER = "smtp.gmail.com"
PORT = 587
SENDER_EMAIL = "2dtankdiploma@gmail.com"
APP_PASSWORD = "nejgklwyqrtucdzf"

app = FastAPI()

# --- Статичні файли ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# --- При запуску створюється таблиця users (аналог CREATE IF NOT EXISTS) ---
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/index.html")

# --- Спрощене оброблення всіх .html сторінок через змінну ---
@app.get("/{page_name}", response_class=HTMLResponse)
async def serve_page(request: Request, page_name: str):
    return templates.TemplateResponse(page_name, {"request": request})

# --- Модель користувача для валідації ---
class UserRegister(BaseModel):
    name: str
    password: str

# --- Реєстрація користувача: замінено SQLite на асинхронну роботу з PostgreSQL ---
@app.post("/register")
async def register_user(request: Request, email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    async with async_session() as session:
        result = await session.execute(select(User).filter((User.email == email) | (User.name == name)))
        existing_user = result.scalars().first()

        if existing_user:
            if existing_user.email == email and existing_user.name == name:
                return JSONResponse(content={"message": "Користувач із такою електронною адресою та псевдонімом уже існує.", "status": "error"}, status_code=400)
            elif existing_user.email == email:
                return JSONResponse(content={"message": "Користувач із цією електронною адресою вже існує.", "status": "error"}, status_code=400)
            elif existing_user.name == name:
                return JSONResponse(content={"message": "Користувач із таким псевдонімом уже існує.", "status": "error"}, status_code=400)

        new_user = User(name=name, email=email, password=password)
        session.add(new_user)
        await session.commit()
        return JSONResponse(content={"message": "Користувач успішно зареєстрований", "status": "success"}, status_code=201)

# --- Авторизація користувача: також замінено на async/await ---
@app.post("/login")
async def login_user(name: str = Form(...), password: str = Form(...)):
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.name == name, User.password == password))
        user = result.scalars().first()

        if user:
            return JSONResponse(content={
                "message": "Login successful",
                "name": user.name,
                "email": user.email
            })
        else:
            return JSONResponse(content={"message": "Invalid login or password"}, status_code=401)

# --- Відновлення пароля (залишено як було, тільки async для запиту до БД) ---
@app.post("/recover-password")
async def recover_password(name: str = Form(...), email: str = Form(...)):
    async with async_session() as session:
        result = await session.execute(select(User).filter(User.name == name, User.email == email))
        user = result.scalars().first()

        if not user:
            return JSONResponse(content={"message": "Користувача не знайдено."}, status_code=404)

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
            return JSONResponse(content={"message": "Пароль успішно надіслано."})
        except Exception as e:
            return JSONResponse(content={"message": f"Помилка надсилання: {str(e)}"}, status_code=500)

# --- Надсилання баг-репорту (залишено без змін) ---
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

# --- Змінено порт на 10000 (рекомендований Render) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)



