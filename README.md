# 2D Tanki Server

🎮 **2D Tanki Server** — це серверна частина багатокористувацької гри на танках, створена з використанням FastAPI. Проєкт включає обробку авторизації, профілів гравців, рейтингової системи та завантаження рівнів.

---

## 🚀 Запуск проєкту

### 1. Клонування репозиторію

```bash
git clone https://github.com/Maxsoson/2D_TANKS_SERVER.git
cd 2D_TANKS_SERVER
```

### 2. Створення та активація віртуального середовища

```bash
python -m venv venv
```

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```

### 3. Встановлення залежностей

```bash
pip install -r installation.txt
```

### 4. Запуск сервера

```bash
uvicorn main:app --reload
```

---

## 📁 Структура проєкту

```
2D_TANKS_SERVER/
├── main.py                  # Запуск FastAPI сервера
├── database/
│   └── users.db             # SQLite база даних користувачів
├── static/                  # Статичні файли: CSS, JS, Images, Audio
│   ├── CSS/
│   ├── JavaScript/
│   ├── Images/
│   └── Audio/
├── templates/               # HTML шаблони (реєстрація, авторизація, гра тощо)
├── installation.txt         # Список залежностей
└── README.md                # Цей файл
```

---

## 🧩 Технології

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- SQLite
- HTML/CSS/JS

---

## 📬 Зворотний зв'язок

Якщо ви знайшли помилку або маєте пропозицію — створіть issue або зробіть pull request 🙌