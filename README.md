# Professional Student Management System (Decoupled Architecture)

A modern, responsive, and secure **Student Management System (SMS)** built with a **Decoupled Architecture**:
* **Backend (`backend/`)**: Python Django REST Framework (DRF) API with Token Authentication, SQLite/PostgreSQL/MySQL support, Excel exporter, and PDF grade sheet generator.
* **Frontend (`frontend/`)**: Modern, high-performance static Single Page Application (HTML5, CSS3, ES6 JavaScript, Chart.js) ready for instant deployment on **Netlify**.

---

## Architecture Overview

```
student-management/
├── backend/                  <-- Deploy to RENDER (Python Web Service)
│   ├── manage.py
│   ├── requirements.txt      <-- Django, DRF, CORS, Gunicorn, WhiteNoise, etc.
│   ├── build.sh              <-- Auto-migration & collectstatic script
│   ├── render.yaml           <-- Render Blueprint configuration
│   ├── config/               <-- Settings, URLs, WSGI
│   ├── api/                  <-- REST API serializers, views, router
│   ├── accounts/             <-- User authentication & profiles
│   ├── departments/          <-- Department models & views
│   ├── courses/              <-- Course models & views
│   ├── students/             <-- Student models & views
│   ├── results/              <-- Semester examination models & PDF generator
│   └── templates/            <-- PDF generation templates
│
├── frontend/                 <-- Deploy to NETLIFY (Static Web Host)
│   ├── index.html            <-- Login & Student Self-Registration portal
│   ├── admin.html            <-- Admin Dashboard with Chart.js & full CRUD
│   ├── student.html          <-- Student Dashboard & Semester Grade Viewer
│   ├── netlify.toml          <-- Netlify headers & redirect rules
│   ├── _redirects            <-- Clean SPA route rewrites
│   ├── css/
│   │   └── styles.css        <-- Glassmorphism & custom light/dark design system
│   └── js/
│       ├── config.js         <-- API Base URL configuration
│       ├── api.js            <-- Fetch HTTP client with Token Auth
│       ├── auth.js           <-- Session manager & toasts
│       └── admin.js          <-- Admin analytics & CRUD modals
│
├── .gitignore                <-- Ignores .venv, db.sqlite3, staticfiles, etc.
└── render.yaml               <-- Root blueprint for Render deployment
```

---

## Default Access Credentials

Seeded records contain the following accounts for immediate evaluation:

### Administrator Account
* **Username**: `admin`
* **Password**: `adminpassword`

### Student Account (Jane Doe)
* **Username**: `2026CSE001`
* **Password**: `studentpassword`

---

## Local Development Setup

### 1. Run the Backend API (Port 8000)
```powershell
cd backend
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver 127.0.0.1:8000
```

### 2. Run the Frontend (Port 3000)
In a separate terminal:
```powershell
cd frontend
python -m http.server 3000
```
Open your browser at **`http://127.0.0.1:3000`**.

---

## Deployment Guide

### A. Deploy Backend to Render

1. Push your repository to **GitHub**.
2. Log in to [dashboard.render.com](https://dashboard.render.com).
3. Click **New +** > **Web Service**.
4. Connect your GitHub repository.
5. Configure the following fields:
   * **Root Directory**: `backend`
   * **Runtime**: `Python 3`
   * **Build Command**: `./build.sh`
   * **Start Command**: `gunicorn config.wsgi:application`
6. Add Environment Variables:
   * `PYTHON_VERSION`: `3.13.0`
   * `DEBUG`: `False`
   * `SECRET_KEY`: *(Click Generate)*
   * `ALLOWED_HOSTS`: `.onrender.com`
7. Click **Create Web Service**. Your backend API will be live at `https://your-app.onrender.com`.

---

### B. Deploy Frontend to Netlify

1. Log in to [app.netlify.com](https://app.netlify.com).
2. Click **Add new site** > **Import an existing project**.
3. Connect your **GitHub** account and choose your repository.
4. Configure the build settings:
   * **Base directory**: `frontend`
   * **Build command**: *(leave blank)*
   * **Publish directory**: `frontend` (or `.` relative to base)
5. Click **Deploy site**.
6. Once deployed, open your live Netlify site URL!
7. Click **API Settings** (or the server icon in the top header) and enter your live **Render Backend URL** (e.g. `https://your-app.onrender.com`).
