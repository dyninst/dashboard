from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from ddash.apps.users.models import User

admin.site.register(User, UserAdmin)
