# 🗨️ Ask-Like Website

A Q&A-style web platform where users can post questions, answer others, and interact through a notification system. Built with Django and designed for engaging, community-driven discussions.

---

## 🛠️ Tech Stack
- Backend: Django

- Database: PostgreSQL

- Frontend: Django Templates, HTML, CSS, JavaScript

- Other Tools: Bootstrap, Django Channels 

---

## Features

### Core
- User Authentication – Sign up, log in, and manage your account.

- Ask & Answer Questions – Post questions, answer others, and engage in discussions.

- Question Categories – Organize questions by tags or topics.

- Upvotes/Downvotes – Show appreciation or disagreement with answers.

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

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/django-notifications.git
   cd django-notifications
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   pip install -r Requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
  Run the development server
  ```bash
   daphne -b 127.0.0.1 -p 8000 project.asgi:application
