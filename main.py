from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3

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
    <body>
        <p>Привіт, {name}!</p>
        <p>Ваш пароль для входу: <strong>{user['password']}</strong></p>
        <p>Будь ласка, збережіть його в безпечному місці.</p>
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


# Налаштування SMTP
SMTP_SERVER = "smtp.gmail.com"
PORT = 587
SENDER_EMAIL = "2dtankdiploma@gmail.com"
APP_PASSWORD = "nejgklwyqrtucdzf"  # 🔐 ← твій app password

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
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, SENDER_EMAIL, message.as_string())
        return {"message": "Bug report sent successfully"}
    
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)