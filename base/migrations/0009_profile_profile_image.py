# Generated by Django 3.2.7 on 2023-11-09 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_profile_date_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
