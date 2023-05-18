from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Follow, User


class UserAdmin(ModelAdmin):
    search_fields = ('email', 'username')


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
