# Generated by Django 5.1.6 on 2025-06-04 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0038_booking_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
