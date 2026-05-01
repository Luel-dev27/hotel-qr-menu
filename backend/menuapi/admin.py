from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from .models import Category, MenuItem, Restaurant, Table


User = get_user_model()


class RestaurantAdminForm(forms.ModelForm):
    staff_username = forms.CharField(
        required=False,
        help_text='Optional: create or update this restaurant staff login.',
    )
    staff_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True),
        help_text='Optional: set or reset the password for the staff login above.',
    )
    staff_email = forms.EmailField(required=False)

    class Meta:
        model = Restaurant
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('staff_username', '').strip()
        password = cleaned_data.get('staff_password', '')

        if password and not username:
            raise forms.ValidationError('Enter a staff username when setting a staff password.')
        if username and not password and not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Enter a password when creating a new staff user.')

        return cleaned_data


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    form = RestaurantAdminForm
    list_display = ('name', 'slug', 'currency', 'guest_menu_link', 'staff_workspace_link')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('admins',)
    readonly_fields = ('guest_menu_link', 'staff_workspace_link')
    fieldsets = (
        (None, {
            'fields': (
                'name',
                'slug',
                'tagline',
                'currency',
                'hero_message',
                'admins',
                'guest_menu_link',
                'staff_workspace_link',
            ),
        }),
        ('Create or reset restaurant staff login', {
            'fields': ('staff_username', 'staff_password', 'staff_email'),
            'description': 'Use this to create the username/password that logs in at /admin/<restaurant-slug>.',
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.tables.exists():
            Table.objects.create(
                restaurant=obj,
                number=1,
                label=f'{obj.name} Menu',
                slug=f'{obj.slug}-menu',
            )

        username = form.cleaned_data.get('staff_username', '').strip()
        password = form.cleaned_data.get('staff_password', '')
        email = form.cleaned_data.get('staff_email', '').strip()
        if username:
            user, _created = User.objects.get_or_create(username=username)
            user.email = email or user.email
            user.is_staff = True
            if password:
                user.set_password(password)
            user.save()
            obj.admins.add(user)

    @admin.display(description='Guest menu URL')
    def guest_menu_link(self, obj):
        if not obj or not obj.slug:
            return 'Save the restaurant to create the URL.'
        url = f'/r/{obj.slug}'
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)

    @admin.display(description='Staff workspace URL')
    def staff_workspace_link(self, obj):
        if not obj or not obj.slug:
            return 'Save the restaurant to create the URL.'
        url = f'/admin/{obj.slug}'
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)


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
