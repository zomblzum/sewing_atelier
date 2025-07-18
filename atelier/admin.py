from django.contrib import admin
from .models import Customer, Order

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'phone', 'created_at')
    search_fields = ('last_name', 'first_name', 'phone')
    list_filter = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'price', 'status', 'created_at')
    search_fields = ('title', 'customer__last_name', 'customer__first_name')
    list_filter = ('status', 'created_at')
    raw_id_fields = ('customer',)