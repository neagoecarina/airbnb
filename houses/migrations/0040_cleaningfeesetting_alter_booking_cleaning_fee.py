# Generated by Django 5.1.6 on 2025-06-06 07:51

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('houses', '0039_booking_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='CleaningFeeSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=Decimal('50.00'), max_digits=10)),
            ],
        ),
        migrations.AlterField(
            model_name='booking',
            name='cleaning_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
