# Generated by Django 4.2.7 on 2024-01-12 20:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_rename_adress_location_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.location'),
        ),
    ]
