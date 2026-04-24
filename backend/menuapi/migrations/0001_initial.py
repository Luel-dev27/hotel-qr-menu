from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('order', models.PositiveIntegerField(default=1)),
            ],
            options={'ordering': ['order', 'id']},
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('tagline', models.CharField(max_length=255)),
                ('currency', models.CharField(default='ETB', max_length=16)),
                ('hero_message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField()),
                ('label', models.CharField(max_length=120)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={'ordering': ['number', 'id']},
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('image', models.URLField()),
                ('available', models.BooleanField(default=True)),
                ('spicy', models.BooleanField(default=False)),
                ('featured', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='menu_items', to='menuapi.category')),
            ],
            options={'ordering': ['-featured', 'id']},
        ),
    ]
