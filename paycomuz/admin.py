from django.contrib import admin
from .models import Transaction


# Register your models here.


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', '_id', 'request_id', 'amount', 'state', 'status',)
    list_display_links = ('id',)
    list_filter = ('status',)
    search_fields = ['request_id', 'status', 'id', '_id']


admin.site.register(Transaction, TransactionAdmin)
