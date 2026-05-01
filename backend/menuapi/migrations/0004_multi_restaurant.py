from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def connect_existing_data(apps, _schema_editor):
    User = apps.get_model('auth', 'User')
    Restaurant = apps.get_model('menuapi', 'Restaurant')
    Category = apps.get_model('menuapi', 'Category')
    Table = apps.get_model('menuapi', 'Table')
    MenuItem = apps.get_model('menuapi', 'MenuItem')

    restaurant = Restaurant.objects.order_by('id').first()
    if not restaurant:
        restaurant = Restaurant.objects.create(
            name='Aster Hotel',
            slug='aster-hotel',
            tagline='Fresh plates, fast service, and a beautiful table experience.',
            currency='ETB',
            hero_message='Scan the QR code, explore the menu, and enjoy a smooth dine-in experience.',
        )

    if not restaurant.slug:
        restaurant.slug = 'aster-hotel'
        restaurant.save(update_fields=['slug'])

    Category.objects.filter(restaurant__isnull=True).update(restaurant=restaurant)
    Table.objects.filter(restaurant__isnull=True).update(restaurant=restaurant)
    MenuItem.objects.filter(restaurant__isnull=True).update(restaurant=restaurant)

    for user in User.objects.filter(is_staff=True):
        restaurant.admins.add(user)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('menuapi', '0003_single_hotel_qr'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='slug',
            field=models.SlugField(default='aster-hotel', unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='restaurants', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='category',
            name='restaurant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='menuapi.restaurant'),
        ),
        migrations.AddField(
            model_name='table',
            name='restaurant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='menuapi.restaurant'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='restaurant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='menuapi.restaurant'),
        ),
        migrations.RunPython(connect_existing_data, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='category',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='menuapi.restaurant'),
        ),
        migrations.AlterField(
            model_name='table',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='menuapi.restaurant'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='menuapi.restaurant'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=120),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('restaurant', 'name'), name='unique_category_name_per_restaurant'),
        ),
    ]
