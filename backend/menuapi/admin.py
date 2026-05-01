from django.contrib import admin

from .models import Category, MenuItem, Restaurant, Table


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'currency')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('admins',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.tables.exists():
            Table.objects.create(
                restaurant=obj,
                number=1,
                label=f'{obj.name} Menu',
                slug=f'{obj.slug}-menu',
            )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'order')
    list_filter = ('restaurant',)
    ordering = ('restaurant', 'order')


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('label', 'restaurant', 'number', 'slug')
    list_filter = ('restaurant',)
    prepopulated_fields = {'slug': ('label',)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'price', 'available', 'featured')
    list_filter = ('restaurant', 'category', 'available', 'featured')
    search_fields = ('name', 'description')
