# 🗨️ Ask-Like Website

A Q&A-style web platform where users can post questions, answer others, and interact through a notification system. Built with Django and designed for engaging, community-driven discussions.

---

## 🛠️ Tech Stack
- **Backend**: Django 5.2.4
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: Django Templates, HTML, CSS, JavaScript
- **Real-time**: Django Channels with Redis
- **Media Storage**: AWS S3
- **Deployment**: Render.com
- **Other Tools**: Bootstrap, WhiteNoise, Daphne (ASGI server) 

---

## Features

### Core
- User Authentication – Sign up, log in, and manage your account.

- Ask & Answer Questions – Post questions, answer others, and engage in discussions.

- Like/Unlike answers.

- Follow/Unfollow users 

### Notifications
  #### Real-Time Notifications for:

- New answers to your question.

- Comments on your answers.

- Mentions in questions or answers.

Mark All as Read – Quickly clear your unread notifications.

View All Notifications – Access a history of both read and unread notifications.

---

## Notification Types Implemented
- **Follow** — triggered when a user follows another.
- **Question Sent** — triggered when a user sends a question.
- **Answer Received** — triggered when someone answers your question.
- **Answer liked** — triggered when a user likes an answer.

---

## 🌐 Live Demo

**Deployed on Render**: [https://ask-hs.onrender.com](https://ask-hs.onrender.com)

The application is deployed on Render with:
- **Database**: Render PostgreSQL
- **Cache**: Render Redis for WebSocket functionality
- **Media Storage**: AWS S3 bucket for profile pictures and media files
- **Static Files**: Served via WhiteNoise
- **WebSocket Server**: Daphne (ASGI) for real-time notifications

---

## 🚀 Deployment Configuration

### Environment Variables (Production)
```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=ask-hs.onrender.com,localhost,127.0.0.1

# Database (Render PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (Render Redis)
REDIS_URL=redis://user:password@host:port

# AWS S3 Media Storage
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=ask-hs-application
AWS_S3_REGION_NAME=eu-north-1
```

### Render Build & Start Commands
- **Build Command**: `pip install -r Requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command**: `daphne -b 0.0.0.0 -p $PORT project.asgi:application`

---

## 💾 Media Storage

The application uses **AWS S3** for media file storage in production:
- **Profile pictures** are automatically uploaded to S3
- **Bucket**: `ask-hs-application` (eu-north-1 region)
- **CDN**: Direct S3 URLs for fast media delivery
- **Fallback**: Local storage for development environment

---

## 🔧 Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ask.hs
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r Requirements.txt
   ```

4. **Environment setup** (create `.env` file)
   ```bash
   SECRET_KEY=your-development-secret-key
   DEBUG=True
   
   # Optional: PostgreSQL (otherwise SQLite will be used)
   DATABASE_URL=postgresql://user:password@localhost:5432/askhs
   
   # Optional: Redis for WebSockets
   REDIS_URL=redis://localhost:6379
   
   # Optional: AWS S3 for media (otherwise local storage)
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_STORAGE_BUCKET_NAME=your-bucket-name
   AWS_S3_REGION_NAME=us-east-1
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   # For basic functionality
   python manage.py runserver
   
   # For WebSocket support (recommended)
   daphne -b 127.0.0.1 -p 8000 project.asgi:application
   ```
