# Generated by Django 4.2.19 on 2025-03-01 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0017_rename_earnings_houseearning_house_earnings_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='houseearning',
            name='house',
        ),
        migrations.DeleteModel(
            name='YearlyEarning',
        ),
        migrations.DeleteModel(
            name='HouseEarning',
        ),
    ]
