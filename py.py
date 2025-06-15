
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
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
import hashlib

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

@app.get("/reset_password.html", response_class=HTMLResponse)
async def reset_password(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

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

def generate_user_id():
    return ''.join(random.choices("0123456789ABCDEF", k=5))

def generate_code(length=6):
    return ''.join(random.choices("0123456789", k=length))

def get_db_connection():
    conn = sqlite3.connect("database/users.db")
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Створення таблиці
with get_db_connection() as db:
    # users
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            recovery_code TEXT
        )
    """)
    # progress
    db.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id TEXT NOT NULL,
            level INTEGER NOT NULL,
            score INTEGER NOT NULL,
            stars INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    # progress_summary
    db.execute("""
        CREATE TABLE IF NOT EXISTS progress_summary (
            user_id TEXT PRIMARY KEY,
            total_score INTEGER NOT NULL,
            total_stars INTEGER NOT NULL,
            levels TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    db.commit()

def save_progress(user_id: str, score: int, stars: int, level: int):
    with get_db_connection() as db:
        cursor = db.cursor()
        print(f"🔧 save_progress: {user_id=}, {score=}, {stars=}, {level=}")

        # Перевірка, чи користувач справді існує
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        if cursor.fetchone() is None:
            print(f"❌ user_id {user_id} not found in users table. Skipping save.")
            return

        # Додати прогрес
        cursor.execute("""
            INSERT INTO progress (user_id, level, score, stars)
            VALUES (?, ?, ?, ?)
        """, (user_id, level, score, stars))

        # Оновлення summary
        cursor.execute("SELECT score, stars, level FROM progress WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()

        total_score = sum(r["score"] for r in rows)
        total_stars = sum(r["stars"] for r in rows)
        levels = sorted({r["level"] for r in rows})
        levels_str = ",".join(str(lvl) for lvl in levels)
        print(f"📘 Calculated levels_str: {levels_str}")

        cursor.execute("SELECT 1 FROM progress_summary WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE progress_summary
                SET total_score = ?, total_stars = ?, levels = ?
                WHERE user_id = ?
            """, (total_score, total_stars, levels_str, user_id))
        else:
            cursor.execute("""
                INSERT INTO progress_summary (user_id, total_score, total_stars, levels)
                VALUES (?, ?, ?, ?)
            """, (user_id, total_score, total_stars, levels_str))

        db.commit()

# приклад: після завершення рівня
class VictoryData(BaseModel):
    user_id: str
    score: int
    stars: int
    level: int

@app.post("/game/victory")
def game_victory(data: VictoryData):
    print(f"[VICTORY] Received: {data.user_id=} {data.score=} {data.stars=} {data.level=}")
    save_progress(data.user_id, data.score, data.stars, data.level)
    return {"status": "saved"}

@app.post("/register")
async def register_user(request: Request, email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Тільки пароль хешується
    hashed_password = hash_value(password)
    user_id = generate_user_id()

    try:
        cursor.execute("""
            INSERT INTO users (user_id, name, email, password)
            VALUES (?, ?, ?, ?)
        """, (user_id, name, email, hashed_password))
        conn.commit()
        return JSONResponse(content={
            "message": "Користувач успішно зареєстрований",
            "status": "success",
            "user_id": user_id
        }, status_code=201)
    except sqlite3.IntegrityError:
        return JSONResponse(content={"message": "Користувач з таким email або іменем уже існує.", "status": "error"}, status_code=400)
    finally:
        conn.close()

@app.post("/login")
async def login_user(name: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_value(password, user["password"]):
        return JSONResponse(content={
            "message": "Login successful",
            "name": user["name"],
            "email": user["email"],
            "user_id": user["user_id"] 
        })

    return JSONResponse(content={"message": "Invalid login or password"}, status_code=401)

@app.get("/profile/{user_id}")
def get_profile(user_id: str):
    with get_db_connection() as db:
        cursor = db.cursor()

        # Отримати name і email з users
        cursor.execute("SELECT name, email FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return JSONResponse(status_code=404, content={"message": "User not found"})

        # Отримати загальний бал з progress_summary
        cursor.execute("SELECT total_score FROM progress_summary WHERE user_id = ?", (user_id,))
        summary = cursor.fetchone()
        total_score = summary["total_score"] if summary else 0

        # Знайти місце в рейтингу
        cursor.execute("SELECT user_id FROM progress_summary ORDER BY total_score DESC")
        all_users = cursor.fetchall()
        place = next((i + 1 for i, row in enumerate(all_users) if row["user_id"] == user_id), None)

        return {
            "email": user["email"],
            "name": user["name"],
            "score": total_score,
            "place": place or "-"
        }

@app.get("/leaderboard")
def get_leaderboard():
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT u.name AS nickname, s.total_score
            FROM progress_summary AS s
            JOIN users AS u ON s.user_id = u.user_id
            ORDER BY s.total_score DESC
        """)
        results = cursor.fetchall()
        return [dict(row) for row in results]

@app.post("/recover-password")
async def recover_password(name: str = Form(...), email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    users = cursor.fetchall()

    for user in users:
        if name == user["name"]:
            code = generate_code()
            cursor.execute("UPDATE users SET recovery_code = ? WHERE email = ?", (code, email))
            conn.commit()
            conn.close()

            message = MIMEMultipart("alternative")
            message["From"] = SENDER_EMAIL
            message["To"] = email
            message["Subject"] = "Код для відновлення пароля"
            html = f""" . . . """

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
async def verify_code(request: Request, name: str = Form(...), code: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT recovery_code FROM users WHERE name = ?", (name,))
        row = cursor.fetchone()

        if row and row["recovery_code"] == code:
            return JSONResponse(content={"message": "Код підтверджено."}, status_code=200)
        else:
            return JSONResponse(content={"message": "Невірний код підтвердження."}, status_code=400)
    finally:
        conn.close()
    
@app.post("/reset-password")
async def reset_password(
    user_id: str = Form(...),
    recovery_code: str = Form(...),
    new_password: str = Form(...)
):
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(new_password)
        cursor.execute("""
            UPDATE users 
            SET password = ?, recovery_code = NULL 
            WHERE user_id = ? AND recovery_code = ?
        """, (hashed_password, user_id, recovery_code))
        conn.commit()

        if cursor.rowcount == 0:
            return JSONResponse(status_code=404, content={"message": "Invalid code or user not found."})

        return JSONResponse(status_code=200, content={"message": "Password updated successfully."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Internal error: {e}"})

    finally:
        conn.close()

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

    html = f"""  . . .  """

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
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
