# SparkLens — Project Walkthrough

> A complete end-to-end guide on how **SparkLens** was built — from zero to production-ready Django app.

---

## Table of Contents

1. [The Vision](#1-the-vision)
2. [Architecture Decisions](#2-architecture-decisions)
3. [Step 1 — Project Setup](#3-step-1--project-setup)
4. [Step 2 — Django Settings](#4-step-2--django-settings)
5. [Step 3 — Data Models](#5-step-3--data-models)
6. [Step 4 — AI Service Layer](#6-step-4--ai-service-layer)
7. [Step 5 — Forms & Validation](#7-step-5--forms--validation)
8. [Step 6 — Views & Routing](#8-step-6--views--routing)
9. [Step 7 — Admin Panel](#9-step-7--admin-panel)
10. [Step 8 — UI Design System](#10-step-8--ui-design-system)
11. [Step 9 — Templates](#11-step-9--templates)
12. [Step 10 — PDF Generation](#12-step-10--pdf-generation)
13. [Step 11 — Production Ready](#13-step-11--production-ready)
14. [How It All Flows Together](#14-how-it-all-flows-together)

---

## 1. The Vision

**Problem:** Founders waste weeks/months building ideas nobody wants. They need fast, honest validation before investing time and money.

**Solution:** Paste a startup idea → AI analyzes it → get a structured professional report with SWOT, scores, risks, and next steps. No signup, no cost, instant results.

**Key Requirements:**
- Production-ready from day one
- No login barrier — session-based history
- Beautiful UI that feels premium
- PDF export for sharing
- Deployable on Railway/Render

---

## 2. Architecture Decisions

| Decision | Choice | Why |
|---|---|---|
| Framework | Django | Batteries-included, secure, proven |
| Database | SQLite | Zero config, perfect for MVP |
| Frontend | Django Templates + CSS | No build step, fast to ship |
| AI Provider | OpenRouter (free tier) | Free models, no credit card needed |
| PDF Engine | WeasyPrint | Server-side HTML→PDF, no JS hacks |
| Static Files | WhiteNoise | Simple CDN-free production serving |
| No Celery/Redis | — | MVP doesn't need async — keep it simple |
| No React/Vue | — | Overkill for a single-page flow |

**Project structure pattern:** We use a `config/` package for Django settings (instead of flat `settings.py`) — this is the industry standard for scalable Django projects.

---

## 3. Step 1 — Project Setup

We started by creating the Django project with a custom layout:

```bash
django-admin startproject config .
python manage.py startapp validator
```

Then reorganized into the final structure:

```
idea_validator/
├── config/           # Django project settings
├── validator/        # Main application
├── static/css/       # Static assets
├── requirements.txt  # Dependencies
├── .env.example      # Environment template
├── Procfile          # Deployment config
└── manage.py         # Django CLI
```

We installed the dependencies:
```
django>=4.2,<5.0
python-dotenv>=1.0
requests>=2.31
weasyprint>=60.0
gunicorn>=21.0
whitenoise>=6.6
```

And set up the virtual environment with `python3 -m venv venv`.

---

## 4. Step 2 — Django Settings

**File:** `config/settings.py`

Key decisions made here:

**Environment loading:**
```python
from dotenv import load_dotenv
load_dotenv()
```
This reads `.env` file on startup — secrets never hardcoded.

**Session config:**
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 days
```
Database-backed sessions persist for 2 weeks — enables "no login" history.

**AI configuration:**
```python
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
OPENROUTER_MODEL = 'openai/gpt-oss-120b:free'
MODEL_DISPLAY_NAME = 'SparkLens AI'
```
We separate the raw API model name from the display name shown to users.

**WhiteNoise middleware** added early so static files work in production:
```python
'whitenoise.middleware.WhiteNoiseMiddleware',
```

---

## 5. Step 3 — Data Models

**File:** `validator/models.py`

Two models, clean and focused:

### `IdeaSubmission`
Stores what the user types:
- `id` — UUID primary key (not auto-increment, for professional URLs)
- `session_key` — links submission to browser session (no login needed)
- `title` — optional, for display
- `description` — required, the actual idea
- `audience` — optional target audience
- `industry` — optional category choice

### `AnalysisReport`
Stores the AI's output:
- `submission` — OneToOne link to IdeaSubmission
- `verdict` — GO / CAUTION / NO-GO
- `summary` — AI's written summary
- `market_score` / `feasibility_score` — integers 1-10
- `strengths`, `weaknesses`, `opportunities`, `threats` — JSON arrays
- `risks` — JSON array of `{risk, mitigation}` objects
- `next_steps` — JSON array of action strings
- `model_used` — which AI model generated this
- `generation_ms` — how long the API call took

**Why JSONField?** The AI returns lists and nested objects. JSONField stores them natively in SQLite — no need for separate relationship tables.

---

## 6. Step 4 — AI Service Layer

**File:** `validator/services.py`

This is the brain. All OpenRouter logic lives here — views never touch API code.

### The System Prompt
A carefully engineered prompt that forces the AI to return **only valid JSON** with exact keys. It includes:
- Strict JSON format rules (no markdown, no backticks)
- Exact key requirements and array lengths
- Behavioral instructions (be specific, be honest)

### The `call_openrouter()` Function
```python
def call_openrouter(submission):
```

**Flow:**
1. Checks API key exists → raises friendly error if missing
2. Sends POST to OpenRouter with system + user prompts
3. Handles timeout and network errors → raises `ValueError`
4. Strips markdown code blocks if the model wraps JSON in backticks
5. Parses JSON → validates all required keys exist
6. Normalizes verdict (uppercase, fallback to CAUTION)
7. Clamps scores to 1-10 range
8. Returns clean dict with all data + metadata

**Error handling:** Every failure path raises `ValueError` with user-friendly messages. Views catch these and show them to the user.

---

## 7. Step 5 — Forms & Validation

**File:** `validator/forms.py`

```python
class IdeaForm(forms.ModelForm):
```

Key decisions:
- Description field requires minimum 30 characters (prevents junk submissions)
- Custom placeholder text guides users to write detailed ideas
- Character counter (JS) shows `X / 1500` on the frontend
- Industry dropdown uses the same `INDUSTRY_CHOICES` as the model

---

## 8. Step 6 — Views & Routing

**File:** `validator/views.py`

Five class-based views:

### `HomeView`
- **GET:** Shows the submission form
- **POST:** Validates form → saves submission → calls AI → saves report → redirects to report page
- On AI failure: deletes the orphaned submission, shows error

### `ReportDetailView`
- Shows a single analysis report
- 404 if report doesn't exist

### `ReportPDFView`
- Renders `pdf_report.html` template → converts to PDF via WeasyPrint
- Returns as `Content-Disposition: attachment` with slugified filename

### `HistoryView`
- **GET:** Lists all submissions for current session
- **POST:** Clears all history (deletes submissions, flushes session)

### `HealthView`
- Simple `{"status": "ok"}` JSON — for uptime monitors

### URL Routing
```python
path('', HomeView, name='home')
path('report/<uuid:pk>/', ReportDetailView, name='report_detail')
path('report/<uuid:pk>/pdf/', ReportPDFView, name='report_pdf')
path('history/', HistoryView, name='history')
path('health/', HealthView, name='health')
```

---

## 9. Step 7 — Admin Panel

**File:** `validator/admin.py`

Both models registered with:
- `list_display` — useful columns in the list view
- `list_filter` — sidebar filters for industry, verdict, date
- `search_fields` — search by title or description
- `readonly_fields` — prevent editing of auto-generated data

Accessible at `/admin/` with superuser credentials.

---

## 10. Step 8 — UI Design System

**File:** `validator/templates/validator/base.html`

All styles defined in one place — no external CSS framework needed.

### Color System
```css
--white: #ffffff;
--bg: #f8f9fc;          /* Light gray-blue background */
--surface: #ffffff;     /* Pure white cards */
--accent: #4f46e5;      /* Indigo primary */
--green: #059669;       /* Emerald for success */
--red: #dc2626;         /* Red for danger */
--amber: #d97706;       /* Amber for warning */
```

### Typography
- **Font:** Plus Jakarta Sans — modern, geometric, premium feel
- **Headings:** 800 weight, tight letter-spacing (-0.03em)
- **Body:** 500 weight, generous line-height

### Animation System
| Animation | Effect | Used For |
|---|---|---|
| `fadeInUp` | Slide up + scale bounce | Cards, sections |
| `fadeInDown` | Drop from top | Badges, nav elements |
| `scaleIn` | Pop from small | Error states, empty states |
| `bounceIn` | Elastic overshoot | Verdict badges |
| `slideInLeft` | Slide from left | Titles, risk items |
| `float` | Gentle vertical bob | Hero badge dot |
| `pulse-glow` | Breathing glow | Logo icon |

All animations use `cubic-bezier(0.22, 1, 0.36, 1)` for that premium, snappy feel.

---

## 11. Step 9 — Templates

### `base.html`
The master template. Contains:
- Google Fonts import (Plus Jakarta Sans)
- Complete CSS design system (variables, components, animations)
- Sticky glassmorphism navbar with logo + nav links
- Content block for child templates
- Footer with "Built by AJ" credit

### `home.html`
The landing page:
- Gradient hero text ("Validate your idea **before you build it**")
- Animated floating dot badge ("AI-Powered Analysis")
- Clean card form with labeled fields
- Character counter with color change near limit
- Trust indicators below CTA (Free forever, No signup, Instant results)
- JS: character counter + submit button spinner

### `report.html`
The star of the show:
- **Header card** with top gradient accent line, verdict badge (bounce animation), idea title, date, and PDF download button
- **Summary card** with left accent border and subtle decorative circle
- **Score rings** — SVG circles that animate from 0 to score on page load (calculated via JavaScript with `requestAnimationFrame`)
- **SWOT grid** — 2x2 layout with colored top accent bars, icon badges, and dot-prefixed list items. Each card has hover lift animation.
- **Risk analysis** — red dot indicators with glowing shadow, mitigation strategy labels, hover slide effect
- **Next steps** — numbered badges with accent border, hover indent effect
- **Footer actions** — gradient primary button + outline secondary button

### `history.html`
- Clean vertical list of analysis cards
- Color-coded left indicator bar (green/amber/red)
- Hover effects: card lifts, indicator stretches, arrow slides right
- Empty state with icon + CTA
- "Clear All" button with confirmation dialog

### `pdf_report.html`
- Standalone template (does NOT extend base.html)
- White background, professional print layout
- Gradient purple header with verdict badge
- Gradient multi-color accent line below header
- SWOT grid with colored backgrounds
- "Built by AJ" watermark in footer with gradient text

---

## 12. Step 10 — PDF Generation

**Engine:** WeasyPrint

**How it works:**
1. `ReportPDFView` fetches the report from the database
2. Renders `pdf_report.html` with Django's `render_to_string`
3. Passes HTML string to `weasyprint.HTML(string=...).write_pdf()`
4. Returns PDF as `HttpResponse` with `Content-Disposition: attachment`

**PDF-specific considerations:**
- Template uses inline CSS (no external stylesheets in PDF context)
- `@page` directive sets A4 size with zero margin
- Font loaded via `@import` in the template's `<style>` block
- No JavaScript (PDFs are static)
- Colors use `print-color-adjust: exact` for accurate rendering

**System dependencies** (macOS): `pango`, `cairo`, `gdk-pixbuf` — these are native rendering libraries WeasyPrint wraps.

---

## 13. Step 11 — Production Ready

### Static Files
- `whitenoise` middleware serves static files in production
- `collectstatic` gathers all static into `/staticfiles/`
- CompressedManifestStaticFilesStorage for cache-busting

### Deployment (Procfile)
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
```
- 2 workers — enough for low-traffic app
- Binds to `$PORT` (Railway/Render convention)

### Security
- CSRF protection on all forms
- Session-based auth (no passwords to leak)
- API key in environment, never in code
- `.env` in `.gitignore`
- `DJANGO_DEBUG=False` in production

### Database
- SQLite works fine for low-traffic. For production with multiple instances, swap to PostgreSQL (one settings change).

---

## 14. How It All Flows Together

### User Journey:

```
1. User opens / (home)
   → HomeView.get() renders home.html
   → Beautiful landing page with form

2. User fills form + clicks "Analyse"
   → HomeView.post() receives form data
   → IdeaForm validates (min 30 chars)
   → IdeaSubmission saved with session_key
   → call_openrouter() sends to AI
   → AI returns JSON analysis
   → AnalysisReport saved
   → Redirect to /report/<uuid>/

3. User sees report
   → ReportDetailView.get() loads report
   → report.html renders with animations
   → SVG score rings animate on load
   → Sections fade in with stagger

4. User downloads PDF
   → Clicks "Download PDF"
   → ReportPDFView generates PDF via WeasyPrint
   → Browser downloads file

5. User checks history
   → Navigates to /history/
   → HistoryView lists all session submissions
   → Color-coded cards with verdict badges
   → Can clear all with one click
```

### Data Flow:

```
Browser Form → Django Form → IdeaSubmission (DB)
                                    ↓
                              OpenRouter API
                                    ↓
                              AnalysisReport (DB)
                                    ↓
                              Report Page (UI)
                                    ↓
                              PDF Download (optional)
```

---

## What Makes This Project Special

1. **Zero friction** — No signup, no email, no password. Just paste and go.
2. **Session persistence** — 14-day cookie remembers your history.
3. **Professional output** — The report looks like a consultant wrote it.
4. **Error resilient** — Every failure point has a user-friendly message.
5. **Production ready** — Gunicorn, WhiteNoise, Procfile, environment config — deploy in minutes.
6. **Beautiful** — Premium white UI with thoughtful animations that feel alive.
7. **Built by AJ** — Your watermark on every report.

---

> **Built with ❤️ by AJ**
