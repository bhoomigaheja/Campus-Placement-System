# Campus Placement Cell — Enterprise SaaS Platform

An enterprise-grade, scalable, and secure SaaS platform designed to modernize university placement drives. The platform features role-based dashboards for Training & Placement Officers (TPOs), Recruiting Companies, and Students, complete with automated ATS resume compatibility parsing, searchable branch filters, skill tags inventories, and an advanced, zero-replay toast notification architecture.

---

## 🚀 Key Features

* **Unified SaaS Notification Engine:** Centralized, exactly-once toast system with cryptographic render ID tracking and microsecond-level server validation to prevent stale Back-Forward Cache (bfcache) or reload replays.
* **Student Resume Profile & File Handling:** Custom visual resume upload state manager with secure file validation, real-time file upload indicators, and automatic storage-level purge of old resumes upon replacement.
* **Automated ATS Job Matching:** Dynamic algorithmic ranking of candidate profiles against active job criteria to output a real-time compatibility score.
* **Placement Drive Orchestration:** Complete CRUD management of placement drives, scheduling of video interviews with calendar links, and applicant disposition workflows.
* **Searchable Branch Filters & Custom Tagging:** Custom tags-input system with predictive suggestion chips for student skills and Select2-equivalent multi-selects for eligible branches.
* **Submit Locks & Screens Guard:** Real-time prevention of duplicate form submissions and double-click actions with native processing spinners.

---

## 🛠️ Tech Stack

* **Backend Engine:** Django (Python 3.11)
* **Frontend Design:** Vanilla CSS with custom premium tokens, Bootstrap 5.3, Bootstrap Icons, Toastify.js
* **Database Management:** PostgreSQL (Production) / SQLite (Local Dev)
* **Static files & CDN:** WhiteNoise with Manifest caching and Gzip compression
* **Task Queues:** Celery (Redis)
* **Web WSGI Server:** Gunicorn

---

## 📦 Local Installation & Setup

Follow these steps to run the application locally on your machine:

### 1. Clone & Navigate to Directory
```bash
git clone <your-repository-url>
cd "campus placement cell"
```

### 2. Configure Virtual Environment
```bash
python -m venv venv
# On Windows (PowerShell/CMD):
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the root directory using the template:
```bash
cp .env.example .env
```

### 5. Setup Local Database
```bash
python manage.py migrate
python manage.py create_super_user  # or python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```
Visit the platform at `http://127.0.0.1:8000/`.

---

## ☁️ Render Production Deployment

The project is fully pre-configured for direct, one-click deployments on **Render Web Services** connected to a **Render PostgreSQL** instance.

### 💼 Main Command Options:
* **Build Command:** `./build.sh`
* **Start Command:** `gunicorn campus_placement.wsgi:application`
