# Generated by Django 4.2.7 on 2023-11-28 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_remove_location_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='street',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='street_number',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]