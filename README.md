# Rent Check - NZ Landlord Tool

A simple web application for New Zealand landlords to track rent payments and get alerts when rent is late.

## Features

- User authentication (signup/login)
- Property management
- Bank account integration via Akahu API
- Automated rent tracking
- Email notifications for missed payments
- Mobile-first responsive design

## Project Structure

```
rent-check/
├── backend/                 # Flask API server
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database connection and models
│   └── requirements.txt    # Python dependencies
├── frontend/               # HTML/JS client
│   ├── index.html         # Main page
│   ├── styles.css         # Styling
│   └── app.js             # Frontend logic
├── scripts/               # Utility scripts
│   └── prd.txt           # Product Requirements Document
└── .env.example          # Environment variables template
```

## Quick Start

### Backend Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
cp ../.env.example .env
# Edit .env with your database and API credentials
```

4. Run the application:
```bash
python app.py
```

### Frontend Setup

Simply open `frontend/index.html` in a web browser or serve with a static server.

### Database Setup

1. Install PostgreSQL
2. Create a database named `rentcheck`
3. Update DATABASE_URL in .env
4. Run database initialization:
```bash
cd backend
python database.py
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key for sessions
- `AKAHU_CLIENT_ID/SECRET`: Akahu API credentials
- `MAIL_*`: Email server configuration

## Development

- Backend runs on `http://localhost:5000`
- Frontend can be served statically or via live server
- API health check available at `/health`

## Tech Stack

- **Backend**: Flask, PostgreSQL, psycopg2
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: PostgreSQL
- **Integration**: Akahu Banking API
- **Email**: SMTP (configurable provider)