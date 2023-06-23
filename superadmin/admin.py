from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


# Register your models here.
class AdminInline(admin.StackedInline):
    model= AdminUser


class CustomizeUser(UserAdmin):
    inlines = (AdminInline, )

admin.site.unregister(User)
admin.site.register(User, CustomizeUser)



admin.site.register(Customer)
admin.site.register(Properties)
admin.site.register(Client)
admin.site.register(Notification)