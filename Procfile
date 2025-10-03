# Procfile for Railway, Heroku, or similar platforms
release: python3 manage.py migrate && python3 manage.py collectstatic --noinput
web: gunicorn community_packing_list.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 60 --access-logfile - --error-logfile -
