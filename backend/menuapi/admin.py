from django.contrib import admin

from .models import Category, MenuItem, Restaurant, Table


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('label', 'number', 'slug')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available', 'featured')
    list_filter = ('category', 'available', 'featured')
    search_fields = ('name', 'description')
