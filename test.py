from fastapi import FastAPI, Request, Form
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
from passlib.context import CryptContext
import random

app = FastAPI()
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

@app.get("/load_to_game_3.html", response_class=HTMLResponse)
async def load_to_game_3(request: Request):
    return templates.TemplateResponse("load_to_game_3.html", {"request": request})

@app.get("/tanki.html", response_class=HTMLResponse)
async def tanki(request: Request):
    return templates.TemplateResponse("tanki.html", {"request": request})

now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

SMTP_SERVER = "smtp.gmail.com"
PORT = 587
SENDER_EMAIL = "2dtankdiploma@gmail.com"
APP_PASSWORD = "nejgklwyqrtucdzf"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_value(value: str) -> str:
    return pwd_context.hash(value)

def verify_value(plain_value: str, hashed_value: str) -> bool:
    return pwd_context.verify(plain_value, hashed_value)

def generate_code(length=6):
    return ''.join(random.choices("0123456789", k=length))

def get_db_connection():
    conn = sqlite3.connect("database/users.db")
    conn.row_factory = sqlite3.Row
    return conn

# Створення таблиці
with get_db_connection() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            recovery_code TEXT
        )
    """)
    db.commit()

@app.post("/register")
async def register_user(request: Request, email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_name = hash_value(name)
    hashed_password = hash_value(password)

    try:
        cursor.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)", (email, hashed_name, hashed_password))
        conn.commit()
        return JSONResponse(content={"message": "Користувач успішно зареєстрований", "status": "success"}, status_code=201)
    except sqlite3.IntegrityError:
        return JSONResponse(content={"message": "Користувач з таким email уже існує.", "status": "error"}, status_code=400)
    finally:
        conn.close()

@app.post("/login")
async def login_user(name: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    for user in users:
        if verify_value(name, user["name"]) and verify_value(password, user["password"]):
            return JSONResponse(content={
                "message": "Login successful",
                "name": name,
                "email": user["email"]
            })

    return JSONResponse(content={"message": "Invalid login or password"}, status_code=401)

@app.post("/recover-password")
async def recover_password(name: str = Form(...), email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    users = cursor.fetchall()

    for user in users:
        if verify_value(name, user["name"]):
            code = generate_code()
            cursor.execute("UPDATE users SET recovery_code = ? WHERE email = ?", (code, email))
            conn.commit()
            conn.close()

            message = MIMEMultipart("alternative")
            message["From"] = SENDER_EMAIL
            message["To"] = email
            message["Subject"] = "Код для відновлення пароля"
            html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="background-color: #000000; font-family: 'Courier New', monospace; color: #00FF00; padding: 30px; margin: 0;">
                <div style="max-width: 600px; margin: auto; border: 2px solid #00FF00; border-radius: 8px; background-color: #111111; padding: 20px; font-size: 18px; line-height: 1.6;">

                    <h1 style="text-align: center; font-size: 32px; margin-bottom: 10px; color: #00FF00;">🔐 Verification code 🔐</h1>

                    <div class="content">
                        <p>Greetings!</p>
                        <p>Your verification code:</p>
                        <div style="background-color: #000; border: 2px dashed #00FF00; padding: 16px; text-align: center; font-size: 22px; font-weight: bold; border-radius: 5px; margin: 20px 0; color: #39ff14;">
                            {code}
                        </div>
                        <p>Enter it in the game to confirm access to your account.</p>
                    </div>

                    <div class="footer" style="text-align: center; font-size: 14px; color: #888; margin-top: 30px;">
                        <p>If you did not request confirmation, simply ignore this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            message.attach(MIMEText(html, "html"))

            try:
                with smtplib.SMTP(SMTP_SERVER, PORT) as server:
                    server.starttls()
                    server.login(SENDER_EMAIL, APP_PASSWORD)
                    server.sendmail(SENDER_EMAIL, email, message.as_string())
                return JSONResponse(content={"message": "Код надіслано на пошту."})
            except Exception as e:
                return JSONResponse(content={"message": f"Помилка надсилання: {str(e)}"}, status_code=500)

    conn.close()
    return JSONResponse(content={"message": "Користувача не знайдено."}, status_code=404)

@app.post("/verify-code")
async def verify_code(email: str = Form(...), code: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT recovery_code FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row and row["recovery_code"] == code:
        return JSONResponse(content={"message": "Код підтверджено. Можна змінити пароль."})
    else:
        return JSONResponse(content={"message": "Неправильний код"}, status_code=401)

@app.post("/change-password")
async def change_password(email: str = Form(...), new_password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_value(new_password)
    cursor.execute("UPDATE users SET password = ?, recovery_code = NULL WHERE email = ?", (hashed_password, email))
    conn.commit()
    conn.close()
    return JSONResponse(content={"message": "Пароль успішно змінено."})

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