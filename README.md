# Professional Student Management System

A modern, responsive, and secure **Student Management System (SMS)** built with Python, Django, Bootstrap 5, and MySQL / PostgreSQL (with seamless SQLite fallback).

---

## Project Structure (Clean Frontend & Backend Separation)

The project separates presentation assets and server logic into dedicated directories without altering any application UI or workflow:

```text
student-management-system/
├── frontend/                     # All Presentation & UI Assets
│   ├── static/                   # Static files
│   │   ├── css/styles.css        # Custom responsive styles & Dark/Light mode theme
│   │   └── js/main.js            # Theme toggle, client interactions, alert timeouts
│   └── templates/                # Django HTML templates (Bootstrap 5)
│       ├── accounts/             # Login, Register, Profile, Change Password
│       ├── courses/              # Course list & course creation/edit forms
│       ├── dashboards/           # Admin Analytics Dashboard & Student Portal
│       ├── departments/          # Department management views
│       ├── results/              # Results publication & PDF gradesheet view
│       ├── students/             # Student directory, CRUD, & detail views
│       ├── base.html             # Base layout template
│       ├── 404.html              # Custom 404 Error page
│       └── 500.html              # Custom 500 Error page
│
├── backend/                      # All Django Server Logic & Configuration
│   ├── accounts/                 # User authentication, RBAC decorators & profiles
│   ├── courses/                  # Course models, views, and forms
│   ├── departments/              # Department models, views, and forms
│   ├── results/                  # Results computation, SGPA/CGPA engine & PDF generator
│   ├── students/                 # Student directory, CRUD & Excel exporter
│   ├── config/                   # Django settings, ASGI, WSGI, URLs
│   ├── build.sh                  # Render production build script
│   ├── render.yaml               # Render Infrastructure as Code configuration
│   ├── requirements.txt          # Production Python dependencies
│   ├── .env.example              # Environment variables template
│   └── manage.py                 # Backend-scoped CLI entrypoint
│
├── manage.py                     # Root CLI entrypoint (runs all commands seamlessly from root)
├── requirements.txt              # Root dependencies pointer
├── .env.example                  # Root environment variables template
├── .gitignore                    # Git ignore rules for Python, SQLite, media, env
└── README.md                     # Project documentation
```

---

## Features

- **Role-Based Access Control (RBAC)**: Secure separation between **Admin** and **Student** views.
- **Admin Dashboard**: Visual analytics (Student distribution chart using Chart.js), total counters, recent student logs, and quick action controls.
- **Student Dashboard**: Welcome cards, personal/academic summaries, and latest semester scores.
- **Student Directory CRUD**: Register, edit, delete, and view detailed profiles (including profile photo uploads).
- **Academic Management**: Manage departments, courses, and publish/edit semester results.
- **Smart Result Computations**: Automatic calculation of total marks, grades, SGPA, and cumulative CGPA based on credits during results publication.
- **Advanced Export Utilities**:
  - Export the student directory list to styled Excel spreadsheets (`openpyxl`).
  - Download official semester gradesheets as PDF files (`xhtml2pdf`).
- **Interactive UI**: Custom Light/Dark theme toggle (saved via LocalStorage), page loading overlays, responsive sidebar, print-optimized stylesheet views, and auto-fading notification alerts.
- **Robust Security**: Built-in CSRF protection, SQL injection prevention (Django ORM), session-based login decorators, and hashed password credentials.
- **Custom Error Routing**: Fully custom, styled 404 (Page Not Found) and 500 (Internal Server Error) templates.

---

## Technology Stack

- **Backend**: Python 3.x, Django 5.x+, Django ORM, MySQL/PostgreSQL/SQLite, PyMySQL, Gunicorn, WhiteNoise.
- **Frontend**: HTML5, CSS3, JavaScript (ES6), Bootstrap 5, Font Awesome 6 Icons, Chart.js.
- **File Generators**: `openpyxl` (Excel), `xhtml2pdf` / `reportlab` (PDF).

---

## Installation & Setup

### 1. Set Up Virtual Environment
Ensure Python 3.x is installed, then create and activate a virtual environment:
```bash
# Create venv
python -m venv .venv

# Activate venv (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate venv (macOS/Linux)
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Configuration (Dynamic)
By default, the project runs on **SQLite** for zero-setup execution. 

To switch to **MySQL**:
1. Make sure your local MySQL server is running.
2. Create a `.env` file in the workspace root folder and fill in your database details:
```env
DB_NAME=student_management_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
DEBUG=True
SECRET_KEY=your_custom_secret_key
```
*(Note: If using MySQL, create the database `CREATE DATABASE student_management_db;` in your MySQL console before running migrations.)*

### 4. Run Migrations
Run schema migrations from either the project root or the `backend/` directory:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Mock Data (Admins, Students, Results)
Rather than starting from scratch, seed the database with sample data:
```bash
python manage.py seed_data
```

### 6. Start the Server
```bash
python manage.py runserver
```
Visit the application at `http://127.0.0.1:8000/`.

---

## Default Access Credentials

Seeded records contain the following accounts for immediate evaluation:

### Administrator Account
- **Username**: `admin`
- **Password**: `adminpassword`

### Student Account (Jane Doe)
- **Username**: `2026CSE001`
- **Password**: `studentpassword`
*(This student has active semester results to inspect CGPA metrics, download gradesheets, and export PDFs.)*

---

## Running Automated Tests

Run the test suite using Django's test manager to verify authentication checks, routing, and access boundaries:
```bash
python manage.py test
```
*(Runs 22 comprehensive unit and integration tests across accounts, departments, courses, students, and results.)*
