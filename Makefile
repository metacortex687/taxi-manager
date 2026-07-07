.PHONY: start-vite docker-build run-dev collectstatic migrate build

K6_SCRIPT ?= load_test_rps_ladder_simple.js

start-vite:
	echo "Starting Vite watcher..."
	cd /home/taxi-manager/taxi_manager/infrastructure/react_frontend && npm run dev -- --host 0.0.0.0

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
	uv run gunicorn taxi_manager.infrastructure.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --access-logfile -

run-gunicorn:
	uv run gunicorn taxi_manager.infrastructure.wsgi:application --bind 0.0.0.0:8000 --workers 2 --worker-class gthread --threads 4 --timeout 120 --access-logfile -

run-asgi:
	uv run gunicorn taxi_manager.infrastructure.asgi:application --workers=2 --worker-class uvicorn_worker.UvicornWorker  --bind 0.0.0.0:8000 --timeout 120 --graceful-timeout 30 --access-logfile - --error-logfile -

ensure-superuser:
	uv run manage.py ensure_superuser

ensure-demo-data:
	uv run manage.py ensure_demo_data

demo-up:
	docker compose -f docker-compose.demo.yaml up --build

dev-up:
	docker compose \
		-p taxi-manager \
		-f docker-compose.dev-local.observability.yaml \
		-f docker-compose.dev-local.yaml \
		up -d --build --force-recreate --remove-orphans

dev-down:
	docker compose -f docker-compose.dev-local.yaml down
	docker compose -f docker-compose.dev-local.observability.yaml down

perf-dev:
	docker compose \
		-p taxi-manager \
		-f docker-compose.dev-local.observability.yaml \
		-f docker-compose.dev-local.yaml \
		-f docker-compose.dev-local.load-testing.yaml \
		run --rm load-generator \
		run \
		-o experimental-prometheus-rw \
		--summary-export /results/summary.json \
		/scripts/$(K6_SCRIPT)

perf-f-observ:
	docker compose \
		-f docker-compose.dev.observability.yaml \
		-f docker-compose.dev.observability.load-testing.yaml \
		run --rm load-generator \
		run \
		-o experimental-prometheus-rw \
		--summary-export /results/summary.json \
		/scripts/$(K6_SCRIPT)

demo-down:
	docker compose -f docker-compose.demo.yaml down

demo-drop-db:
	docker compose -f docker-compose.demo.yaml down -v

run-uwsgi:
	uv run uwsgi --ini /app/uwsgi.ini

#Системные зависимости для GeoDjango
install-geo-deps:
	apt-get update
	apt-get install -y --no-install-recommends \
		binutils \
		gdal-bin \
		libgdal-dev \
		libgeos-dev \
		libproj-dev
	rm -rf /var/lib/apt/lists/*

install-geo-deps-ci:
	sudo apt-get update
	sudo apt-get install -y --no-install-recommends \
		binutils \
		gdal-bin \
		libgdal-dev \
		libgeos-dev \
		libproj-dev
	sudo rm -rf /var/lib/apt/lists/*

run-vk-bot:
	uv run manage.py run_vk_bot

run-pgwatch-listener:
	uv run manage.py pgwatch_listen --consumers vk_bot_trip_change
