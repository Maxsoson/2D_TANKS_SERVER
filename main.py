from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# Підключення статичних файлів
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/CSS", StaticFiles(directory="static/CSS"), name="CSS")
app.mount("/JavaScript", StaticFiles(directory="static/JavaScript"), name="JavaScript")
app.mount("/Images", StaticFiles(directory="static/Images"), name="Images")

# Підключення шаблонів HTML
templates = Jinja2Templates(directory="templates")

# Маршрут для кореневої сторінки (автоматичне перенаправлення на index.html)
@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/index.html")

# Головна сторінка
@app.get("/index.html", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Інші сторінки
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
        <p><strong>Subject:</strong><b>{subject}</b></p>
        <p><strong>Message:</strong>{msg}</p>
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
