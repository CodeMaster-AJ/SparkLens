# Installation Notes

## WeasyPrint System Dependencies

WeasyPrint requires native libraries for PDF generation. Install them before running the app.

### macOS (Homebrew)

```bash
brew install pango cairo gdk-pixbuf libffi
```

### Ubuntu/Debian

```bash
sudo apt-get install libpango-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libffi-dev
```

### Fedora

```bash
sudo dnf install pango cairo gdk-pixbuf2 libffi-devel
```

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install system dependencies for WeasyPrint (see above)

# 4. Set up environment
cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY

# 5. Run migrations
python manage.py makemigrations validator
python manage.py migrate

# 6. Create superuser (optional, for admin)
python manage.py createsuperuser

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Run development server
python manage.py runserver
```

## Deployment (Railway/Render)

Both platforms provide the required system libraries by default. No extra buildpacks needed.

1. Connect your GitHub repo
2. Set environment variables: `DJANGO_SECRET_KEY`, `OPENROUTER_API_KEY`, `DJANGO_DEBUG=False`
3. Build command: `python manage.py collectstatic --noinput && python manage.py migrate`
4. Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
