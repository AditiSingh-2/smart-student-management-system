# Smart Student Management System

A university-level student management system with AI-powered email classification.

## Features
- Role-based access (Admin, Teacher, Student)
- Attendance tracking with warnings
- Internal marks and exam schedule
- Fee status management
- Smart email classification (AI + rule-based)
- Gmail integration via OAuth 2.0
- CI/CD pipeline with GitHub Actions

## Tech Stack
- Backend: Django 3.2.6, Python 3.9
- Database: SQLite
- Frontend: Bootstrap, AdminLTE
- AI: Claude API (Anthropic)
- Email: Gmail API (Google OAuth 2.0)

## Setup Instructions

### 1. Clone the repo
git clone https://github.com/AditiSingh-2/smart-student-management-system
cd smart-student-management-system

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

### 3. Install dependencies
pip install -r requirements.txt

### 4. Environment variables
Create a .env file in root:
CLAUDE_API_KEY=your_claude_api_key_here

### 5. Gmail API Setup (optional)
- Go to https://console.cloud.google.com
- Create project and enable Gmail API
- Download credentials.json and place in root folder
- See docs for full OAuth setup

### 6. Run migrations
python manage.py migrate

### 7. Create superuser
python manage.py createsuperuser

### 8. Run server
python manage.py runserver

## Note
credentials.json, token.json, and .env are not included for security.