# Generated by Django 4.2.7 on 2023-11-28 10:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0022_rename_street_location_street_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='adress',
            new_name='address',
        ),
    ]