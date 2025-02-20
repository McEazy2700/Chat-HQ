echo "Collecting staticfiles"
python manage.py collectstatic --no-input

echo "Migrating Database"
python manage.py migrate --no-input

echo "Start Server"
python manage.py runserver 0.0.0.0:${BACKEND_PORT}
