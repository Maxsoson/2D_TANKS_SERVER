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
app.mount("/CSS", StaticFiles(directory="static/CSS"), name="CSS")
app.mount("/JavaScript", StaticFiles(directory="static/JavaScript"), name="JavaScript")
app.mount("/Images", StaticFiles(directory="static/Images"), name="Images")

# Підключення шаблонів HTML
templates = Jinja2Templates(directory="templates")

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
        #return RedirectResponse(url="/leaderboard.html", status_code=302)
        return JSONResponse(content={
            "message": "Login successful",
            "token": "example_token",
            "username": user["name"]  # Має бути user["name"], а не null
        })
    else:
        return JSONResponse(content={"message": "Invalid nickname or password"}, status_code=401)

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
    
    