# Generated by Django 5.1.6 on 2025-02-25 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='price',
            field=models.IntegerField(null=True),
        ),
    ]
