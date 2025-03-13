from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import jwt
import datetime
import bcrypt

app = FastAPI()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Підключення статичних файлів
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/CSS", StaticFiles(directory="static/CSS"), name="CSS")
app.mount("/JavaScript", StaticFiles(directory="static/JavaScript"), name="JavaScript")
app.mount("/Images", StaticFiles(directory="static/Images"), name="Images")

# Підключення шаблонів HTML
templates = Jinja2Templates(directory="templates")

# Функція для підключення до бази даних із `check_same_thread=False` та `timeout=10`
def get_db_connection():
    conn = sqlite3.connect("database/users.db", check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# Налаштування SQLite в WAL-режим
with get_db_connection() as conn:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.commit()

# Створення таблиці users при запуску сервера
with get_db_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()

# Модель для реєстрації користувачів
class UserRegister(BaseModel):
    email: str
    name: str
    password: str

# Функція хешування паролів
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Функція перевірки пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# Маршрут для реєстрації користувачів
@app.post("/register")
async def register_user(email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    hashed_password = hash_password(password)  # Хешуємо пароль перед збереженням

    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)", 
                           (email, name, hashed_password))
            conn.commit()
            return {"message": "The user is successfully registered"}
        except sqlite3.IntegrityError:
            return {"message": "A user with this email or nickname already exists."}

# Функція для перевірки користувача (за name + password)
def authenticate_user(name: str, password: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        user = cursor.fetchone()

    if user and verify_password(password, user["password"]):  # Перевірка хешованого пароля
        return user
    return None

# Маршрут для авторизації (вхід за name + password)
@app.post("/login")
async def login(name: str = Form(...), password: str = Form(...)):
    user = authenticate_user(name, password)

    if not user:
        return JSONResponse(status_code=400, content={"message": "❌ Невірний nickname або пароль"})

    # Генерація JWT-токена
    token_data = {
        "sub": user["name"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)  # Термін дії 12 годин
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"message": "✅ Вхід успішний!", "token": token, "username": user["name"]}

# Маршрути сторінок
@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/index.html")

@app.get("/index.html", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/load1.html", response_class=HTMLResponse)
async def load1(request: Request):
    return templates.TemplateResponse("load1.html", {"request": request})

@app.get("/load2.html", response_class=HTMLResponse)
async def load2(request: Request):
    return templates.TemplateResponse("load2.html", {"request": request})

@app.get("/register.html", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/bug_report.html", response_class=HTMLResponse)
async def bug_report(request: Request):
    return templates.TemplateResponse("bug_report.html", {"request": request})

@app.get("/leaderboard.html", response_class=HTMLResponse)
async def leaderboard(request: Request):
    return templates.TemplateResponse("leaderboard.html", {"request": request})

# Налаштування SMTP для надсилання баг-репортів
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
        <p><strong>Subject:</strong> {subject} </p>
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
