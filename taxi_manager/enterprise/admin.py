from django.contrib import admin
from .models import Enterprise
# Register your models here.

class EnterpriseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "city",
    )

admin.site.register(Enterprise, EnterpriseAdmin)
