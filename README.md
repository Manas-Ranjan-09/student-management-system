# Professional Student Management System

A modern, responsive, and secure **Student Management System (SMS)** built with Python, Django, Bootstrap 5, and MySQL (with seamless SQLite fallback).

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

- **Backend**: Python 3.x, Django 5.x+, Django ORM, MySQL/SQLite, PyMySQL.
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
2. Create a `.env` file in the workspace root folder (`student_management/`) and fill in your database details:
```env
DB_NAME=student_management_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
DEBUG=True
SECRET_KEY=your_custom_secret_key
```
*(Note: If you use MySQL, ensure you create the database `CREATE DATABASE student_management_db;` in your MySQL console before running migrations.)*

### 4. Run Migrations
Run the schema setup commands:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed Mock Data (Admins, Students, Results)
Rather than starting from scratch, seed the database with high-quality sample data:
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
