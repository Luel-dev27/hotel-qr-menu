from django.db import migrations


def ensure_single_hotel_qr(apps, _schema_editor):
    Table = apps.get_model('menuapi', 'Table')

    primary_table, _created = Table.objects.update_or_create(
        slug='hotel-menu',
        defaults={
            'number': 1,
            'label': 'Hotel Menu',
        },
    )

    Table.objects.exclude(id=primary_table.id).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('menuapi', '0002_seed_sample_data'),
    ]

    operations = [
        migrations.RunPython(ensure_single_hotel_qr, migrations.RunPython.noop),
    ]
