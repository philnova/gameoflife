web: gunicorn gameoflife:app.flask_app --log-file -
migrate: alembic upgrade head
upgrade: alembic upgrade +1
downgrade: alembic downgrade -1