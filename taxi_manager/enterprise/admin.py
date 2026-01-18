from django.contrib import admin
from .models import Enterprise, Manager
# Register your models here.

class EnterpriseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "city",
    )

class ManagerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "enterprise",
        "user",
    )

admin.site.register(Enterprise, EnterpriseAdmin)
admin.site.register(Manager, ManagerAdmin)