# Generated by Django 4.2.19 on 2025-03-01 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0016_yearlyearning_houseearning'),
    ]

    operations = [
        migrations.RenameField(
            model_name='houseearning',
            old_name='earnings',
            new_name='house_earnings',
        ),
        migrations.RenameField(
            model_name='yearlyearning',
            old_name='total_earnings',
            new_name='yearly_earnings',
        ),
    ]
