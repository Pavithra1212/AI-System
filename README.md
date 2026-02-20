# 🔍 AI Powered Campus Lost & Found System

A production-ready, mobile-first web application for managing lost and found items on campus with AI-powered matching.

## ✨ Features

- **AI Matching** — Automatic similarity scoring using OpenCV (image) + TF-IDF (text)
- **Real-Time Updates** — WebSocket-powered admin dashboard with instant report notifications
- **Premium UI** — Glassmorphism, smooth animations, mobile-first responsive design
- **Role-Based Auth** — JWT authentication with student and admin roles
- **Smart Filtering** — Filter by section, time period, status, and type

## 🚀 Quick Start

### Prerequisites
- Python 3.11+

### Setup

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd PROJECT

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Run the server
cd backend
uvicorn app.main:app --reload --port 8000
```

### Access
- **App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 👤 Default Accounts

| Role | Username | Password |
|------|----------|----------|
| Student | 727625BIT116 | MCET12345 |
| Student | 727625BIT120 | MCET12345 |
| Student | 727625BIT280 | MCET12345 |
| Student | 727625BIT390 | MCET12345 |
| Admin | ADMINMCET | ADMIN12345 |

## 🐳 Docker

```bash
docker-compose up --build
```

## 🚀 Deployment

### Railway (Recommended)

1. Push your repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Set the following environment variables in Railway dashboard:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | A long random string (e.g. `openssl rand -hex 32`) |
| `DEBUG` | `false` |
| `ALLOWED_ORIGINS` | Your Railway URL, e.g. `https://myapp.up.railway.app` |

> Railway automatically sets `PORT`. No need to configure it manually.

4. Deploy — Railway detects the `Dockerfile` and builds automatically.

### Render

1. Push to GitHub → Connect on [render.com](https://render.com)
2. Choose **Web Service** → **Docker** environment
3. Set the same env vars as Railway above
4. Render sets `PORT` automatically

### Heroku

```bash
heroku create my-campus-lf
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
heroku config:set DEBUG=false
heroku config:set ALLOWED_ORIGINS=https://my-campus-lf.herokuapp.com
git push heroku main
```

### Any Docker Host

```bash
docker build -t campus-lf .
docker run -d -p 8000:8000 \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  -e DEBUG=false \
  -e ALLOWED_ORIGINS=https://yourdomain.com \
  campus-lf
```

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** (prod) | — | JWT signing key |
| `PORT` | No | `8000` | Server port (set by platform) |
| `DEBUG` | No | `false` | Enable debug mode |
| `DATABASE_URL` | No | `sqlite:///./lost_found.db` | Database connection string |
| `ALLOWED_ORIGINS` | No | `*` | Comma-separated CORS origins |
| `MATCH_THRESHOLD` | No | `0.70` | AI match confidence threshold |
| `IMAGE_WEIGHT` | No | `0.4` | Image similarity weight |
| `TEXT_WEIGHT` | No | `0.6` | Text similarity weight |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `480` | JWT expiry |
| `MAX_UPLOAD_SIZE` | No | `5242880` | Max upload size (bytes) |

## 📁 Project Structure

```
PROJECT/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # JWT authentication
│   │   ├── seed.py              # User seeding
│   │   ├── websocket_manager.py # Real-time WebSocket
│   │   ├── routes/              # API endpoints
│   │   ├── services/            # Business logic
│   │   └── utils/               # AI matching utilities
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Login page
│   ├── student.html             # Student dashboard
│   ├── admin.html               # Admin dashboard
│   ├── css/styles.css           # Design system
│   └── js/                      # Client-side logic
├── Dockerfile
├── docker-compose.yml
├── railway.toml
├── Procfile
└── .env.example
```

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------| 
| Backend | FastAPI, SQLAlchemy, Uvicorn |
| Auth | JWT (python-jose), bcrypt |
| AI | OpenCV, scikit-learn, NumPy |
| Frontend | Vanilla JS, Alpine.js, Custom CSS |
| Real-Time | WebSockets |
| Database | SQLite (dev) / PostgreSQL (prod) |

## 📄 License

MIT
