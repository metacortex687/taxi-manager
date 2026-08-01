from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from taxi_manager.infrastructure.users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    readonly_fields = (*DjangoUserAdmin.readonly_fields, "uuid")

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Дополнительно", {"fields": ("uuid",)}),
    )