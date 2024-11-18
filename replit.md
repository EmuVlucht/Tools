# M-Mail - Temporary Email Web Application

## Overview
Aplikasi web full-stack untuk membuat dan mengelola email sementara (temporary email). Dibangun dengan Flask (Python) backend dan frontend modern menggunakan HTML/CSS/JavaScript.

## Project Structure
```
.
├── app.py              # Flask backend application
├── models.py           # SQLAlchemy database models
├── templates/
│   └── index.html      # Frontend HTML template
├── static/
│   ├── css/
│   │   └── style.css   # Modern CSS styling
│   └── js/
│       └── app.js      # Frontend JavaScript
├── Procfile            # Railway/Heroku deployment
├── railway.json        # Railway configuration
├── nixpacks.toml       # Nixpacks build configuration
└── mmail/              # Original CLI application (reference)
```

## Technology Stack
- **Backend**: Flask 3.1.2, Flask-SQLAlchemy, Flask-CORS
- **Database**: PostgreSQL (Railway)
- **Frontend**: HTML5, CSS3 (Custom modern design), JavaScript (Vanilla)
- **Deployment**: Gunicorn WSGI server, Railway

## Features
1. **Create Random Email** - Generate random temporary email
2. **Create Custom Email** - Choose email name and domain
3. **Inbox Check** - Auto-refresh inbox every 5 seconds
4. **View Messages** - Read full email content with attachments
5. **Email History** - All created emails saved to database
6. **Copy Email** - One-click copy email address

## Database Schema
- **temp_emails**: Stores created email addresses with tokens
- **email_messages**: Stores received email messages

## API Endpoints
- `GET /` - Frontend web application
- `GET /health` - Health check endpoint
- `GET /api/domains` - Get available email domains
- `POST /api/email/create/random` - Create random email
- `POST /api/email/create/custom` - Create custom email
- `GET /api/emails` - List all emails
- `GET /api/email/<id>` - Get email details
- `GET /api/email/<id>/inbox` - Check inbox for new messages
- `DELETE /api/email/<id>` - Delete email
- `POST /api/email/<id>/activate` - Reactivate expired email

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Server port (default: 5000)
- `SECRET_KEY` - Flask secret key (optional)

## Railway Deployment
Project sudah dikonfigurasi untuk deploy ke Railway:
1. Push repository ke GitHub
2. Connect repository ke Railway
3. Set `DATABASE_URL` environment variable
4. Deploy!

## Development
```bash
# Run locally
python app.py

# Production (with gunicorn)
gunicorn app:app --bind 0.0.0.0:5000 --workers 2
```

## Recent Changes
- **Dec 2024**: Converted from CLI to full-stack web application
- **Dec 2024**: Added PostgreSQL database integration
- **Dec 2024**: Created modern responsive frontend
- **Dec 2024**: Configured Railway deployment
