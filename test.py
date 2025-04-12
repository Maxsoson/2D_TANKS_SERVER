from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3

from datetime import datetime

import logging
from http import HTTPStatus

# Клас фільтрує записи, які містять "ConnectionResetError"
class ConnectionResetFilter(logging.Filter):
    def filter(self, record):
        return 'ConnectionResetError' not in record.getMessage()

# Додаємо фільтр до логера Uvicorn
logging.getLogger("uvicorn.error").addFilter(ConnectionResetFilter())

app = FastAPI()

    # Поточний час
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Налаштування SMTP
SMTP_SERVER = "smtp.gmail.com"
PORT = 587
SENDER_EMAIL = "2dtankdiploma@gmail.com"
APP_PASSWORD = "nejgklwyqrtucdzf"  # 🔐 ← твій app password

# Підключення статичних файлів
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Маршрути сторінок
@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/index.html")

@app.get("/index.html", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register.html", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/bug_report.html", response_class=HTMLResponse)
async def bug_report(request: Request):
    return templates.TemplateResponse("bug_report.html", {"request": request})

@app.get("/leaderboard.html", response_class=HTMLResponse)
async def leaderboard(request: Request):
    return templates.TemplateResponse("leaderboard.html", {"request": request})

@app.get("/load_to_game_1.html", response_class=HTMLResponse)
async def load_to_game_1(request: Request):
    return templates.TemplateResponse("load_to_game_1.html", {"request": request})

@app.get("/load_to_game_2.html", response_class=HTMLResponse)
async def load_to_game_2(request: Request):
    return templates.TemplateResponse("load_to_game_2.html", {"request": request})

@app.get("/tanki.html", response_class=HTMLResponse)
async def tanki(request: Request):
    return templates.TemplateResponse("tanki.html", {"request": request})

# Функція для підключення до бази даних
def get_db_connection():
    conn = sqlite3.connect("database/users.db")
    conn.row_factory = sqlite3.Row
    return conn

# Створення таблиці users при запуску сервера
with get_db_connection() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    db.commit()

# Модель для отримання даних
class UserRegister(BaseModel):
    name: str
    password: str

# Маршрут для реєстрації користувачів
@app.post("/register")
async def register_user(request: Request, email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)", (email, name, password))
        conn.commit()
        return JSONResponse(content={"message": "Користувач успішно зареєстрований", "status": "success"}, status_code=201)
    #The user is successfully registered
    
    except sqlite3.IntegrityError:
        cursor.execute("SELECT * FROM users WHERE email = ? OR name = ?", (email, name))
        existing_user = cursor.fetchone()

        if existing_user:
            if existing_user["email"] == email and existing_user["name"] == name:
                return JSONResponse(content={"message": "Користувач із такою електронною адресою та псевдонімом уже існує.", "status": "error"}, status_code=400)
            #A user with this email and nickname already exists.
            elif existing_user["email"] == email:
                return JSONResponse(content={"message": "Користувач із цією електронною адресою вже існує.", "status": "error"}, status_code=400)
            #A user with this email already exists.
            elif existing_user["name"] == name:
                return JSONResponse(content={"message": "Користувач із таким псевдонімом уже існує.", "status": "error"}, status_code=400)
    #A user with this nickname already exists.
    
    finally:
        conn.close()


# Маршрут для авторизації користувачів
@app.post("/login")
async def login_user(name: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE name = ? AND password = ?", (name, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return JSONResponse(content={
            "message": "Login successful",
            "name": user["name"],
            "email": user["email"]
        })
    else:
        return JSONResponse(content={"message": "Invalid login or password"}, status_code=401)

# Маршрут для відновлення пароля
@app.post("/recover-password")
async def recover_password(name: str = Form(...), email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE name = ? AND email = ?", (name, email))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return JSONResponse(content={"message": "Користувача не знайдено."}, status_code=404)

    # 💡 ЗАМІСТЬ TO_EMAIL — використовуємо email користувача
    message = MIMEMultipart("alternative")
    message["From"] = SENDER_EMAIL
    message["To"] = email  # ✅ ← ВАЖЛИВО!
    message["Subject"] = "Відновлення паролю"

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
        body {{
            background-color: #000000;
            font-family: 'Courier New', monospace;
            color: #00FF00;
            padding: 30px;
            margin: 0;
        }}
        .container {{
            max-width: 600px;
            margin: auto;
            border: 2px solid #00FF00;
            border-radius: 8px;
            background-color: #111111;
            padding: 20px;
            font-size: 18px;
            line-height: 1.6;
        }}
        h1 {{
            text-align: center;
            font-size: 32px;
            margin-bottom: 25px;
            color: #00FF00;
        }}
        .optional-image {{
            display: block;
            max-width: 100%;
            height: auto;
            margin: 0 auto 20px;
            border-radius: 8px;
            border: 2px solid #00FF00;
        }}
        .content {{
            color: #d0ffd0;
            font-size: 18px;
        }}
        .password-box {{
            background-color: #000;
            border: 2px dashed #00FF00;
            padding: 16px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            border-radius: 5px;
            margin: 20px 0;
            color: #39ff14;
        }}
        .footer {{
            text-align: center;
            font-size: 14px;
            color: #888;
            margin-top: 30px;
        }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Відновлення паролю</h1>

            <!-- Опціональне зображення -->
            <img src="https://i.ibb.co/ZVJ2yNz/logo.png" alt="Game Logo" class="optional-image">

            <div class="content">
                <p>Привіт, {name}!</p>
                <p>Ваш пароль для входу:</p>
                <div class="password-box">{user['password']}</div>
                <p>Будь ласка, збережіть його в безпечному місці.</p>
            </div>

            <div class="footer">
                <p>Якщо ви не запитували відновлення паролю, просто ігноруйте цей лист.</p>
            </div>
        </div>
    </body>
    </html>
    """



    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, PORT) as server:
            server.starttls()  # 🛡️ Не забудь!
            server.login(SENDER_EMAIL, APP_PASSWORD)  #✅
            server.sendmail(SENDER_EMAIL, email, message.as_string())  # ✅ ← Надсилаємо на email користувача
        return JSONResponse(content={"message": "Пароль успішно надіслано."})
    except Exception as e:
        return JSONResponse(content={"message": f"Помилка надсилання: {str(e)}"}, status_code=500)

# Маршрут для форми bug_report
@app.post("/send-bug-report")
async def send_bug_report(
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    msg: str = Form(...)
):
    message = MIMEMultipart('alternative')
    message['From'] = SENDER_EMAIL
    message['To'] = SENDER_EMAIL  # 📩 Надсилаємо розробнику
    message['Subject'] = f'Bug Report: {subject}'

    html = f"""
    <html>
    <body style="background-color: #000000; font-family: 'Courier New', monospace; color: #00FF00; padding: 30px;">
        <div style="max-width: 600px; margin: auto; border: 2px solid #00FF00; border-radius: 8px; padding: 20px; background-color: #111111; font-size: 18px; line-height: 1.6;">

        <h1 style="text-align: center; font-size: 32px; margin-bottom: 25px; color: #00FF00;">🛠 BUG REPORT</h1>

        <div style="margin-bottom: 20px;">
            <p style="margin: 0; color: #39ff14; font-size: 20px;"><strong>Name:</strong></p>
            <div style="border: 2px solid #00FF00; padding: 12px; border-radius: 4px; background-color: #000; color: #d0ffd0; font-size: 18px;">
            {name}
            </div>
        </div>

        <div style="margin-bottom: 20px;">
            <p style="margin: 0; color: #39ff14; font-size: 20px;"><strong>Email:</strong></p>
            <div style="border: 2px solid #00FF00; padding: 12px; border-radius: 4px; background-color: #000; color: #d0ffd0; font-size: 18px;">
            {email}
            </div>
        </div>

        <div style="margin-bottom: 20px;">
            <p style="margin: 0; color: #39ff14; font-size: 20px;"><strong>Subject:</strong></p>
            <div style="border: 2px solid #00FF00; padding: 12px; border-radius: 4px; background-color: #000; color: #d0ffd0; font-size: 18px;">
            {subject}
            </div>
        </div>

        <div>
            <p style="margin: 0; color: #39ff14; font-size: 20px;"><strong>Message:</strong></p>
            <div style="background-color: #222; border: 2px dashed #00FF00; padding: 16px; border-radius: 4px; white-space: pre-wrap; color: #d0ffd0; font-size: 18px;">
            {msg}
            </div>
        </div>

        <div style="margin-top: 30px;">
            <p style="margin: 0; color: #39ff14; font-size: 20px;"><strong>Report Timestamp:</strong></p>
            <div style="border: 2px solid #00FF00; padding: 12px; border-radius: 4px; background-color: #000; color: #d0ffd0; font-size: 18px;">
            {now}
            </div>
        </div>

        <p style="margin-top: 35px; font-size: 14px; text-align: center; color: #888;">This message was auto-generated by Pixel Tanks Battlefront</p>
        </div>
    </body>
    </html>
    """


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
    uvicorn.run(app, host="127.0.0.1", port=8000)