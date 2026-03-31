from taxi_manager.settings import *

DATABASES = DATABASES.copy()

DATABASES["import_target"] = DATABASES["default"].copy()
DATABASES["import_target"]["NAME"]="taxi_manager_import"
