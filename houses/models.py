from django.db import models
from django.utils import timezone

# Create your models here.
# houses/models.py

from django.db import models
from django.utils import timezone


class House(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Booking(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=255, default="Unknown")
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Booking for {self.house.name} by {self.customer_name}"