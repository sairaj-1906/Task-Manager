<div align="center">

<img src="static/images/taskflow-mark.svg" alt="Taskflow logo" width="84" />

# Taskflow

### Make space for what matters.

A clean, fast and secure task manager built with **Django**, featuring user accounts, a personal dashboard and a polished light/dark interface.

<br />

[![Live Demo](https://img.shields.io/badge/Live_Demo-Open_App-4f46e5?style=for-the-badge&logo=vercel&logoColor=white)](https://task-manager-two-dusky-41.vercel.app/login/?next=/)
[![Source Code](https://img.shields.io/badge/GitHub-Source_Code-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sairaj-1906/Task-Manager)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-Backend-092E20?style=flat-square&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-UI-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Vercel](https://img.shields.io/badge/Deployed_on-Vercel-000000?style=flat-square&logo=vercel&logoColor=white)
![Render](https://img.shields.io/badge/Database_on-Render-46E3B7?style=flat-square&logo=render&logoColor=white)

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Screenshots](#-screenshots)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment)
- [Task API](#task-api)
- [Deadline email alerts](#deadline-email-alerts)
- [Automated tests and CI](#automated-tests-and-ci)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Author](#-author)

---

## Overview

**Taskflow** is a full-stack task management web application that helps you plan your work and stay focused. Create an account, sign in, and manage everything from a single, distraction-free dashboard.

The project is built with Django's batteries-included approach (authentication, ORM, templating, security middleware) and is deployed to production with a managed PostgreSQL database.

> **Try it now:** [task-manager-two-dusky-41.vercel.app](https://task-manager-two-dusky-41.vercel.app/login/?next=/)

---

## Features

- **User authentication:** sign up, log in and log out with Django's secure auth system.
- **Personal dashboard:** a focused view of your tasks, available only after you sign in.
- **Task planning:** priorities, due dates, categories, and editable tags.
- **Task discovery:** search, filter by status/priority/category/tag, and sort by title, priority, date, or creation time.
- **Deadline alerts:** dashboard alerts for due-today, due-tomorrow, and overdue tasks, plus scheduled email reminders.
- **REST API:** authenticated JSON endpoints for listing, creating, reading, updating, and deleting tasks.
- **Automated checks:** Django tests and configuration/migration checks run in GitHub Actions on pushes and pull requests.
- **Light and dark mode:** a theme toggle in the navbar for comfortable use day or night.
- **Responsive design:** a clean interface that works on desktop, tablet and mobile.
- **Production-ready:** environment-based configuration, WhiteNoise static files and PostgreSQL support.
- **Secure by default:** CSRF protection, password hashing and login-required views.

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Language** | Python 3.12 |
| **Framework** | Django |
| **Database** | PostgreSQL (production) / SQLite (local development) |
| **Frontend** | Django Templates, custom CSS, vanilla JavaScript |
| **Static files** | WhiteNoise |
| **Server** | Gunicorn / Vercel Python runtime |
| **Hosting** | Vercel (app) and Render (PostgreSQL) |
| **Version control** | Git and GitHub |

---

## Screenshots

> Add your screenshots to a `docs/` folder and update the paths below.

| Login | Dashboard |
| :---: | :---: |
| ![Login page](docs/login.png) | ![Dashboard](docs/dashboard.png) |

| Dark Mode | Mobile |
| :---: | :---: |
| ![Dark mode](docs/dark-mode.png) | ![Mobile view](docs/mobile.png) |

---

## Project Structure

```text
Task-Manager/
├── myproject/        # Project settings, URLs, WSGI entry point
├── tasks/            # Main app: models, views, forms, URLs
├── templates/        # HTML templates (base, login, signup, dashboard)
├── static/           # CSS, JavaScript and images
├── manage.py         # Django command-line utility
├── requirements.txt  # Python dependencies
└── .gitignore
```

---

## Getting Started

Follow these steps to run Taskflow on your own machine.

### Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

### 1. Clone the repository

```bash
git clone https://github.com/sairaj-1906/Task-Manager.git
cd Task-Manager
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. (Optional) Create an admin user

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

---

## Environment Variables

Taskflow reads its production configuration from environment variables. For local development, the defaults work out of the box (SQLite database).

| Variable | Description | Example |
| --- | --- | --- |
| `SECRET_KEY` | Django secret key (**required in production**) | `a-long-random-string` |
| `DEBUG` | Enables debug mode. Keep `False` in production | `False` |
| `DATABASE_URL` | PostgreSQL connection string. Falls back to SQLite if unset | `postgresql://USER:PASSWORD@HOST/DBNAME` |

Generate a secure secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> **Never commit secrets.** Keep `.env` files and credentials out of version control.

---

## Deployment

Taskflow is deployed with a modern, free-tier friendly stack:

| Service | Purpose |
| --- | --- |
| **GitHub** | Source control and continuous deployment trigger |
| **Vercel** | Hosts the Django application |
| **Render** | Managed PostgreSQL database |

### Deploy your own copy

1. **Fork** this repository on GitHub.
2. **Create a PostgreSQL database** on [Render](https://render.com) and copy its **External Database URL**.
3. **Import the repo** into [Vercel](https://vercel.com) and add the environment variables `SECRET_KEY`, `DEBUG=False` and `DATABASE_URL`.
4. **Run migrations** once against the production database:

   ```powershell
   # PowerShell
   $env:DATABASE_URL = "your-external-database-url"
   python manage.py migrate
   python manage.py createsuperuser
   Remove-Item Env:DATABASE_URL
   ```

   ```bash
   # macOS / Linux
   DATABASE_URL="your-external-database-url" python manage.py migrate
   ```
5. **Redeploy.** Every push to `main` now deploys automatically.

---

## Task API

The API uses the signed-in user's Django session. Requests that change data must include a valid CSRF token. Staff users can access all tasks; other users can access only their own.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/tasks/` | List tasks; supports `q`, `status`, `priority`, `category`, `tag`, `sort`, `limit` (1–100), and `offset` query parameters |
| `POST` | `/api/tasks/` | Create a task |
| `GET` | `/api/tasks/<id>/` | Retrieve a task |
| `PUT`, `PATCH` | `/api/tasks/<id>/` | Update a task |
| `DELETE` | `/api/tasks/<id>/` | Delete a task |

Example create/update JSON:

```json
{
  "title": "Prepare release",
  "description": "Review the release checklist",
  "category_id": 1,
  "tags": ["Release", "Work"],
  "priority": "HIGH",
  "due_date": "2026-12-01",
  "is_complete": false
}
```

List responses contain `count`, `next_offset`, and `results`. Invalid JSON or fields return a JSON `400`; unauthenticated requests return `401`.

## Deadline email alerts

The dashboard highlights incomplete tasks due today, tomorrow, or earlier. To send email reminders for due-today, due-tomorrow, and overdue tasks, schedule this command to run daily:

```powershell
python manage.py send_task_alerts
```

Configure `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, and `DEFAULT_FROM_EMAIL` in the environment. Without `EMAIL_HOST`, Django's console email backend prints the messages locally. A reminder is recorded after successful delivery so rerunning the command does not resend the same task/date alert.

## Automated tests and CI

Run the test suite locally with:

```powershell
python manage.py test
```

GitHub Actions runs the Django system check, migration consistency check, and tests for each push and pull request.

## Roadmap

- [x] User registration and authentication
- [x] Personal dashboard
- [x] Light / dark theme
- [x] Production deployment (Vercel + PostgreSQL)
- [x] Task priorities and due dates
- [x] Search, filters, and sorting
- [x] Task categories and tags
- [x] REST API
- [x] Automated tests and CI pipeline
- [x] In-app and email deadline alerts

Have an idea? [Open an issue](https://github.com/sairaj-1906/Task-Manager/issues) and let's talk.

---

## Contributing

Contributions, issues and feature requests are welcome!

1. Fork the project
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "Add amazing feature"`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## Author

**Sairaj**

- GitHub: [@sairaj-1906](https://github.com/sairaj-1906)
- Live project: [Taskflow](https://task-manager-two-dusky-41.vercel.app/login/?next=/)

---

<div align="center">

If you found this project useful, please consider giving it a star on GitHub!

**Built with Django and a lot of focus.**

</div>