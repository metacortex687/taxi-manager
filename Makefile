.PHONY: start-vite docker-build run-dev collectstatic migrate build

start-vite:
	echo "Starting Vite watcher..."
	cd /home/taxi-manager/taxi_manager/react_frontend && npm run dev -- --host 0.0.0.0

docker-build:
	docker build --no-cache -t metacortex687/taxi-manager .

docker-run-dev:
	docker run --rm --network host --env-file .env metacortex687/taxi-manager

run-dev:
	uv run manage.py runserver 0.0.0.0:8000

collectstatic:
	uv run manage.py collectstatic --noinput

migrate:
	uv run manage.py migrate --noinput

build:
	make collectstatic && make migrate

run-gunicorn-dev:
	uv run gunicorn taxi_manager.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile -

run-gunicorn:
	uv run gunicorn taxi_manager.wsgi:application --bind 0.0.0.0:8000 --workers 2 --worker-class gthread --threads 4 --timeout 120 --access-logfile -
