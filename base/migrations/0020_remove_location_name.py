# Generated by Django 4.2.7 on 2023-11-27 20:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='name',
        ),
    ]
