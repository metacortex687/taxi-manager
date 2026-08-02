SQLITE_DEMO_DB := demo.db
SQLITE_WORK_DB := /dev/shm/cypress_tests.sqlite3
SETTINGS := --settings=cypress.settings_sqlite_dev


create-sqlite-demo-db-from-fixture:
	uv run ../manage.py shell --no-imports $(SETTINGS) \
		-c 'from django.db import connection; connection.cursor().execute("SELECT InitSpatialMetaData(1)")'

	uv run ../manage.py migrate $(SETTINGS)

	uv run ../manage.py loaddata sqlite_demo_data.json $(SETTINGS)
	

start-sqlite-demo-server:
	rm -f \
		"$(SQLITE_WORK_DB)" \
		"$(SQLITE_WORK_DB)-journal" \
		"$(SQLITE_WORK_DB)-shm" \
		"$(SQLITE_WORK_DB)-wal"

	cp "$(SQLITE_DEMO_DB)" "$(SQLITE_WORK_DB)"

	SQLITE_DB_PATH="$(SQLITE_WORK_DB)" \
		uv run ../manage.py runserver \
			0.0.0.0:8000 \
			$(SETTINGS)


install-spatialite:
	apt update
	apt install -y libsqlite3-mod-spatialite spatialite-bin	
	find /usr/lib -name 'mod_spatialite.so*'

cypress-install:
	npm install cypress --save-dev

cypress-open:
	npx cypress open

cypress-run:
	npx cypress run