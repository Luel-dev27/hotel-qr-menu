from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed_initial_data(apps, _schema_editor):
    User = apps.get_model('auth', 'User')
    Restaurant = apps.get_model('menuapi', 'Restaurant')
    Category = apps.get_model('menuapi', 'Category')
    Table = apps.get_model('menuapi', 'Table')
    MenuItem = apps.get_model('menuapi', 'MenuItem')

    User.objects.update_or_create(
        username='admin',
        defaults={
            'first_name': 'Restaurant',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True,
            'password': make_password('admin123'),
            'email': 'admin@example.com',
        },
    )

    Restaurant.objects.get_or_create(
        id=1,
        defaults={
            'name': 'Aster Hotel',
            'tagline': 'Fresh plates, fast service, and a beautiful table experience.',
            'currency': 'ETB',
            'hero_message': 'Scan the QR code, explore the menu, and enjoy a smooth dine-in experience.',
        },
    )

    categories = {}
    for index, name in enumerate(['Breakfast', 'Starters', 'Main Dishes', 'Drinks', 'Desserts'], start=1):
        category, _ = Category.objects.get_or_create(name=name, defaults={'order': index})
        category.order = index
        category.save()
        categories[name] = category

    tables = [
        {'number': 1, 'label': 'Hotel Menu', 'slug': 'hotel-menu'},
    ]

    for table in tables:
        Table.objects.get_or_create(slug=table['slug'], defaults=table)

    items = [
        {
            'name': 'Abyssinia Breakfast',
            'category': 'Breakfast',
            'price': '290.00',
            'description': 'Eggs, fresh bread, seasonal fruit, coffee, and local honey.',
            'image': 'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?auto=format&fit=crop&w=900&q=80',
            'available': True,
            'spicy': False,
            'featured': True,
        },
        {
            'name': 'Crispy Sambusa Trio',
            'category': 'Starters',
            'price': '250.00',
            'description': 'Three crisp sambusas filled with lentils, beef, and cheese.',
            'image': 'https://images.unsplash.com/photo-1604909052743-94e838986d24?auto=format&fit=crop&w=900&q=80',
            'available': False,
            'spicy': False,
            'featured': False,
        },
        {
            'name': 'Chef Special Tibs',
            'category': 'Main Dishes',
            'price': '640.00',
            'description': 'Tender beef tibs with rosemary butter, peppers, and injera.',
            'image': 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80',
            'available': True,
            'spicy': True,
            'featured': True,
        },
        {
            'name': 'Garden Pasta Bowl',
            'category': 'Main Dishes',
            'price': '520.00',
            'description': 'Creamy pasta with herbs, roasted vegetables, and parmesan.',
            'image': 'https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?auto=format&fit=crop&w=900&q=80',
            'available': True,
            'spicy': False,
            'featured': False,
        },
        {
            'name': 'Berry Sunset Smoothie',
            'category': 'Drinks',
            'price': '220.00',
            'description': 'Strawberry, mango, yogurt, and mint with a chilled finish.',
            'image': 'https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=900&q=80',
            'available': True,
            'spicy': False,
            'featured': False,
        },
        {
            'name': 'Chocolate Lava Slice',
            'category': 'Desserts',
            'price': '260.00',
            'description': 'Warm chocolate cake with vanilla cream and espresso syrup.',
            'image': 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?auto=format&fit=crop&w=900&q=80',
            'available': True,
            'spicy': False,
            'featured': True,
        },
    ]

    for item in items:
        MenuItem.objects.get_or_create(
            name=item['name'],
            defaults={
                'category': categories[item['category']],
                'price': item['price'],
                'description': item['description'],
                'image': item['image'],
                'available': item['available'],
                'spicy': item['spicy'],
                'featured': item['featured'],
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('menuapi', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_initial_data, migrations.RunPython.noop),
    ]
