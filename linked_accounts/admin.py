from django.contrib import admin

from linked_accounts.models import LinkedAccount


class LinkedAccountAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'service']


admin.site.register(LinkedAccount, LinkedAccountAdmin)
