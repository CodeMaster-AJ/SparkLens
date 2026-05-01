# SparkLens

> **Validate startup ideas with AI in seconds.** Get a structured professional analysis with SWOT, market scoring, risk assessment, and actionable next steps.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

---

## Features

- **AI-Powered Analysis** — Paste your startup idea, get a structured report instantly
- **SWOT Analysis** — Strengths, Weaknesses, Opportunities, Threats breakdown
- **Market & Feasibility Scores** — Circular animated score rings out of 10
- **Risk Assessment** — Identified risks with mitigation strategies
- **Actionable Next Steps** — 5 prioritized steps to move forward
- **PDF Export** — Download professional analysis reports
- **Session History** — All past analyses saved automatically, no login needed
- **Premium UI** — Rich white theme with bold animations

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2 |
| AI API | OpenRouter (`openai/gpt-oss-120b:free`) |
| Frontend | Django Templates + CSS (no frameworks) |
| Database | SQLite |
| PDF Export | WeasyPrint |
| Static Files | WhiteNoise |
| Production Server | Gunicorn |

## Quick Start

### 1. Prerequisites

- Python 3.10+
- System libraries for WeasyPrint (PDF generation)

**macOS:**
```bash
brew install pango cairo gdk-pixbuf libffi
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libpango-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libffi-dev
```

### 2. Setup

```bash
# Clone or navigate to the project
cd idea_validator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### 3. Run

```bash
# Run migrations
python manage.py makemigrations validator
python manage.py migrate

# Create superuser (optional, for /admin)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Start the server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | Yes | Django secret key |
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |
| `DJANGO_DEBUG` | No | Set to `False` in production |
| `ALLOWED_HOSTS` | No | Comma-separated host list |

## Project Structure

```
idea_validator/
├── config/                  # Django settings package
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Root URL routing
│   └── wsgi.py              # WSGI application
├── validator/               # Main Django app
│   ├── models.py            # IdeaSubmission & AnalysisReport
│   ├── views.py             # Class-based views
│   ├── services.py          # OpenRouter AI API logic
│   ├── forms.py             # Idea submission form
│   ├── admin.py             # Django admin config
│   ├── urls.py              # App URL routes
│   └── templates/validator/
│       ├── base.html        # Base template + design system
│       ├── home.html        # Landing + submission form
│       ├── report.html      # AI analysis report display
│       ├── history.html     # Past analyses list
│       └── pdf_report.html  # PDF generation template
├── static/css/print.css     # PDF print styles
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway/Render deployment
├── .env.example             # Environment template
└── manage.py                # Django CLI
```

## URL Routes

| URL | View | Description |
|---|---|---|
| `/` | HomeView | Landing page + idea submission form |
| `/report/<uuid>/` | ReportDetailView | View an analysis report |
| `/report/<uuid>/pdf/` | ReportPDFView | Download report as PDF |
| `/history/` | HistoryView | View/clear past analyses |
| `/health/` | HealthView | Health check endpoint |
| `/admin/` | Django Admin | Admin panel |

## Deployment

### Railway / Render

1. Connect your GitHub repository
2. Set environment variables:
   - `DJANGO_SECRET_KEY` (generate a secure key)
   - `OPENROUTER_API_KEY`
   - `DJANGO_DEBUG=False`
3. Build command:
   ```bash
   python manage.py collectstatic --noinput && python manage.py migrate
   ```
4. Start command (auto-detected from `Procfile`):
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
   ```

## Screenshots

### Home Page
Clean white landing page with gradient hero, submission form, and trust indicators.

### Report Page
Professional analysis with animated score rings, SWOT grid with colored accents, risk analysis cards, and numbered next steps — all with staggered entrance animations.

### PDF Export
White-background professional report with gradient header, SWOT grid, and "Built by AJ" watermark.

## License

MIT — Built by **AJ**
