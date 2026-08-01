SQLITE_DB := /dev/shm/cypress_tests.sqlite3
SETTINGS := --settings=cypress.settings_sqlite_dev
SPATIALITE_EXTENSION := /usr/lib/x86_64-linux-gnu/mod_spatialite.so.7.1.0

reset-and-start-sqlite-demo:
	rm -f \
		"$(SQLITE_DB)" \
		"$(SQLITE_DB)-journal" \
		"$(SQLITE_DB)-shm" \
		"$(SQLITE_DB)-wal"

	test ! -e "$(SQLITE_DB)"

	uv run ../manage.py shell --no-imports $(SETTINGS) \
		-c 'from django.db import connection; connection.cursor().execute("SELECT InitSpatialMetaData(1)")'

	uv run ../manage.py migrate geo_tracking 0002 $(SETTINGS)
	uv run ../manage.py migrate geo_tracking 0003 --fake $(SETTINGS)
	uv run ../manage.py migrate $(SETTINGS)

	uv run ../manage.py loaddata sqlite_demo_data.json $(SETTINGS)

# 	uv run ../manage.py loaddata demo_data.json $(SETTINGS)
	uv run ../manage.py runserver 0.0.0.0:8000 $(SETTINGS)

install-spatialite:
	apt update
	apt install -y libsqlite3-mod-spatialite spatialite-bin	
	find /usr/lib -name 'mod_spatialite.so*'

cypress-install:
	npm install cypress --save-dev
 