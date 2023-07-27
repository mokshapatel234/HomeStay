from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


# Register your models here.
class TermsInline(admin.StackedInline):
    model= TermsandPolicy


class CustomizeUser(UserAdmin):
    inlines = (TermsInline, )

admin.site.unregister(User)
admin.site.register(User, CustomizeUser)



admin.site.register(Customer)
admin.site.register(Properties)
admin.site.register(Client)
