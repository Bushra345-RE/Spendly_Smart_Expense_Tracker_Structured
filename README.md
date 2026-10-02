# ✦ Spendly — Smart Expense Tracker

## Project Structure

```text
Spendly/
├── backend/
│   ├── app.py
│   └── models.py
│
├── frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── expenses.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
│
├── venv/
├── database
├── requirements.txt
└── README.md
```

## Run

From the project root:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The SQLite database is the top-level `database` file.
