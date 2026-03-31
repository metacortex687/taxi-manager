from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone


from import_export import resources


class SelectableDBAAliasResourceMixin: #Нужен для тестов, что бы выбирать базу данных
    db_alias: str

    def __init__(self, db_alias: str = "default", **kwargs):
        super().__init__(**kwargs)
        self.db_alias = db_alias

    def get_queryset(self):
        return self._meta.model.objects.using(self.db_alias).all()

    def do_instance_save(self, instance, is_create):
        instance.save(using=self.db_alias)


class TimeZoneResource(SelectableDBAAliasResourceMixin, resources.ModelResource):
    class Meta:
        model = TimeZone
        exclude = ("id",)
        import_id_fields = ("code",)


