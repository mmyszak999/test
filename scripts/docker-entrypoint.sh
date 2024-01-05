python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout

export DJANGO_SETTINGS_MODULE=src.settings

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn django-app.wsgi:application --bind 0.0.0.0:8000 --workers 3
exec "$@"