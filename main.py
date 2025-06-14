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
from passlib.context import CryptContext
import random
import hashlib

app = FastAPI()

# === Статичні файли та шаблони ===
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# === Email конфіг ===
SMTP_SERVER = "smtp.gmail.com"
PORT = 587
SENDER_EMAIL = "2dtankdiploma@gmail.com"
APP_PASSWORD = "nejgklwyqrtucdzf"

# === Хешування ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_value(value: str) -> str:
    return pwd_context.hash(value)
def verify_value(plain_value: str, hashed_value: str) -> bool:
    return pwd_context.verify(plain_value, hashed_value)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# === Генерація ===
def generate_user_id():
    return ''.join(random.choices("0123456789ABCDEF", k=5))
def generate_code(length=6):
    return ''.join(random.choices("0123456789", k=length))

# === БД ===
def get_db_connection():
    conn = sqlite3.connect("database/users.db")
    conn.row_factory = sqlite3.Row
    return conn

# === Створення таблиць ===
with get_db_connection() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            recovery_code TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            level INTEGER NOT NULL,
            score INTEGER NOT NULL,
            stars INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
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

# === СТОРІНКИ ===
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

# === GAME LOGIC ===
class VictoryData(BaseModel):
    user_id: str
    score: int
    stars: int
    level: int

@app.post("/game/victory")
def game_victory(data: VictoryData):
    save_progress(data.user_id, data.score, data.stars, data.level)
    return {"status": "saved"}

def save_progress(user_id: str, score: int, stars: int, level: int):
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        if cursor.fetchone() is None:
            print(f"❌ user_id {user_id} not found.")
            return
        cursor.execute("""
            INSERT INTO progress (user_id, level, score, stars)
            VALUES (?, ?, ?, ?)
        """, (user_id, level, score, stars))
        cursor.execute("SELECT score, stars, level FROM progress WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        total_score = sum(r["score"] for r in rows)
        total_stars = sum(r["stars"] for r in rows)
        levels = sorted({r["level"] for r in rows})
        levels_str = ",".join(str(lvl) for lvl in levels)
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

# === AUTH ===
@app.post("/register")
async def register_user(email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_value(password)
    user_id = generate_user_id()
    try:
        cursor.execute("""
            INSERT INTO users (user_id, name, email, password, recovery_code)
            VALUES (?, ?, ?, ?, NULL)
        """, (user_id, name, email, hashed_password))
        conn.commit()
        return JSONResponse(content={"message": "Registered", "user_id": user_id}, status_code=201)
    except sqlite3.IntegrityError:
        return JSONResponse(content={"message": "User exists"}, status_code=400)
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
        return JSONResponse(content={"message": "Login OK", "user_id": user["user_id"], "name": user["name"], "email": user["email"]})
    return JSONResponse(content={"message": "Invalid credentials"}, status_code=401)

# === leaderboard ===

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

@app.get("/profile/{user_id}")
def get_profile(user_id: str):
    with get_db_connection() as db:
        cursor = db.cursor()

        # 1) Отримати name і email
        cursor.execute("SELECT name, email FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return JSONResponse(status_code=404, content={"message": "User not found"})

        # 2) Отримати загальний бал
        cursor.execute("SELECT total_score FROM progress_summary WHERE user_id = ?", (user_id,))
        summary = cursor.fetchone()
        total_score = summary["total_score"] if summary else 0

        # 3) Знайти місце в рейтингу
        cursor.execute("SELECT user_id FROM progress_summary ORDER BY total_score DESC")
        all_users = cursor.fetchall()
        place = next((i + 1 for i, row in enumerate(all_users) if row["user_id"] == user_id), None)

        return {
            "email": user["email"],
            "name": user["name"],
            "score": total_score,
            "place": place or "-"
        }


# === PASSWORD RECOVERY ===
@app.post("/recover-password")
async def recover_password(name: str = Form(...), email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    users = cursor.fetchall()
    for user in users:
        if name == user["name"]:
            code = generate_code()
            # ОЧИЩАЄМО password і записуємо recovery_code
            cursor.execute("UPDATE users SET recovery_code = ?, password = '' WHERE email = ?", (code, email))
            conn.commit()
            conn.close()

            message = MIMEMultipart("alternative")
            message["From"] = SENDER_EMAIL
            message["To"] = email
            message["Subject"] = "Your Recovery Code"

            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
            </head>
            <body style="background-color: #ffffff; font-family: Arial, sans-serif; color: #333; padding: 40px; max-width: 600px; margin: auto;">

            <h2 style="color: #111111; font-size: 24px;">🔐 Verification Code 🔐</h2>

            <p>Hello,</p>

            <p>Your verification code is:</p>

            <div style="background-color: #f4f4f4; border: 1px solid #cccccc; border-radius: 6px; padding: 16px; text-align: center; font-size: 24px; font-weight: bold; color: #222;">
                {code}
            </div>

            <p style="margin-top: 24px;">
                Enter this code to complete your verification. This code will expire shortly.
            </p>

            <p style="font-size: 13px; color: #888; margin-top: 40px;">
                If you did not request this code, please ignore this message.
            </p>

            <p style="font-size: 13px; color: #888;">
                This message was generated by Pixel Tanks Battlefront.
            </p>

            </body>
            </html>

            """
            message.attach(MIMEText(html, "html"))

            with smtplib.SMTP(SMTP_SERVER, PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.sendmail(SENDER_EMAIL, email, message.as_string())

            return JSONResponse(content={
            "message": "Code sent to email",
            "user_id": user["user_id"],
            "recovery_code": code
        })

    conn.close()
    return JSONResponse(content={"message": "User not found"}, status_code=404)

@app.post("/verify-code")
async def verify_code(name: str = Form(...), code: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT recovery_code FROM users WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row and row["recovery_code"] == code:
        return JSONResponse(content={"message": "Code valid"}, status_code=200)
    return JSONResponse(content={"message": "Invalid code"}, status_code=400)

@app.post("/reset-password")
async def reset_password(
    user_id: str = Form(...),
    recovery_code: str = Form(...),
    new_password: str = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = hash_value(new_password)  # тут твоя функція bcrypt або sha256

    cursor.execute("""
        UPDATE users
        SET password = ?, recovery_code = NULL
        WHERE user_id = ? AND recovery_code = ?
    """, (hashed_password, user_id, recovery_code))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return JSONResponse(status_code=404, content={"message": "Invalid recovery code or user_id"})

    conn.close()
    return JSONResponse(content={"message": "Password updated"})

# === BUG REPORT ===
@app.post("/send-bug-report")
async def send_bug_report(name: str = Form(...), email: str = Form(...), subject: str = Form(...), msg: str = Form(...)):
    message = MIMEMultipart("alternative")
    message["From"] = SENDER_EMAIL
    message["To"] = SENDER_EMAIL
    message["Subject"] = f"Bug Report: {subject}"

    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <body style="font-family: Arial, sans-serif; background-color: #ffffff; color: #333; padding: 40px; max-width: 640px; margin: auto;">

            <h2 style="color: #111;">🛠 Bug Report Submitted</h2>

            <p>Hello,</p>

            <p><strong>{name}</strong> has submitted a bug report for <strong>Pixel Tanks Battlefront</strong>.</p>

            <p>Please find the details below:</p>

            <table style="width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 15px;">
                <tr>
                    <td style="padding: 8px; font-weight: bold; width: 130px;">Name:</td>
                    <td style="padding: 8px;">{name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Email:</td>
                    <td style="padding: 8px;">{email}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Subject:</td>
                    <td style="padding: 8px;">{subject}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold;">Timestamp:</td>
                    <td style="padding: 8px;">{now}</td>
                </tr>
            </table>

        <div style="margin-top: 30px;">
            <p style="font-weight: bold;">Message:</p>
            <div style="background-color: #f3f3f3; border: 1px solid #ccc; padding: 16px; border-radius: 6px; white-space: pre-wrap; font-family: monospace;">
                {msg}
            </div>
            </div>

            <p style="margin-top: 40px; font-size: 13px; color: #777;">
            This message was automatically generated by Pixel Tanks Battlefront.
            </p>

        </body>
        </html>
    """
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_SERVER, PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, SENDER_EMAIL, message.as_string())

    return {"message": "Bug report sent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)