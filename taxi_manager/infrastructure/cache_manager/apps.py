from django.apps import AppConfig

from django.db.backends.signals import connection_created

from taxi_manager.infrastructure.cache_manager.services import CacheManager



class CacheManagerConfig(AppConfig):
    name = 'taxi_manager.infrastructure.cache_manager'

    wrappers = []
    cache_manager = CacheManager()

    def ready(self):
        def print_sql(execute, sql, params, many, context):
            self.cache_manager.clear_if_write_sql(sql)

            return execute(sql, params, many, context)

        def install_wrapper(sender, connection, **kwargs):
            wrapper = connection.execute_wrapper(print_sql)
            wrapper.__enter__()
            self.wrappers.append(wrapper)

        connection_created.connect(install_wrapper)