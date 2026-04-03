#  ExpenseIQ — Python Fullstack Expense Tracker
> **Stack:** Python · Flask · PostgreSQL · SQLAlchemy · HTML · CSS · JavaScript · Chart.js

---

##  Project Structure

```
expense_tracker/
│
├── app.py                  ← Main Flask app (routes, models, logic)
├── requirements.txt        ← Python dependencies
├── .env                    ← Environment variables (DB URL, secret key)
│
└── templates/              ← HTML pages (Jinja2 templates)
    ├── base.html           ← Shared layout (navbar, flash messages)
    ├── login.html          ← Login page
    ├── register.html       ← Register page
    ├── dashboard.html      ← Dashboard with charts
    ├── expenses.html       ← All expenses list + filter
    ├── add_expense.html    ← Add new expense form
    └── edit_expense.html   ← Edit existing expense form
```

---

##  Setup Instructions (Step by Step)

### Step 1 — Install PostgreSQL
Download from https://www.postgresql.org/download/ and install it.

After installing, open **pgAdmin** or **psql** and run:
```sql
CREATE DATABASE expense_tracker;
```

### Step 2 — Clone / Download the project
```bash
cd your-projects-folder
```

### Step 3 — Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Configure environment variables
Open the `.env` file and update:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/expense_tracker
SECRET_KEY=any-random-string-you-want
```
Replace `YOUR_PASSWORD` with your PostgreSQL password.

### Step 6 — Run the app
```bash
python app.py
```

You'll see:
```
 Database tables created successfully.
 * Running on http://127.0.0.1:5000
```

### Step 7 — Open in browser
Go to: **http://127.0.0.1:5000**

---

##  Features

| Feature | Description |
|---|---|
| User Registration & Login | Secure auth with hashed passwords |
| Add / Edit / Delete Expenses | Full CRUD operations |
| Dashboard | Summary cards + interactive charts |
| Category Filter | Filter expenses by category |
| Month Filter | Filter expenses by month |
| Doughnut Chart | Spending by category (Chart.js) |
| Bar Chart | Monthly spending trend (Chart.js) |
| REST API | `/api/category-data` and `/api/monthly-trend` endpoints |
| Responsive UI | Works on mobile and desktop |

---

##  Tech Stack (for your resume)

- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy
- **Database:** PostgreSQL, SQLAlchemy ORM
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
- **Data Viz:** Chart.js
- **Auth:** Werkzeug password hashing, session management
- **Deployment ready:** python-dotenv, environment variables

---

##  How to describe this on your resume

**Project:** ExpenseIQ — Personal Expense Tracker Web Application
- Built a fullstack web app using **Python Flask** and **PostgreSQL** with user authentication (login/register) and session management
- Implemented full **CRUD operations** for expense management with category and date filters
- Developed **REST API endpoints** consumed by the frontend using JavaScript **Fetch API**
- Integrated **Chart.js** for interactive dashboard visualisations (doughnut + bar charts)
- Used **SQLAlchemy ORM** for database modelling and **Werkzeug** for secure password hashing
- Designed a responsive, dark-themed UI using pure **HTML/CSS** with **Jinja2** templating
