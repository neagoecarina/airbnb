from django import forms
from .models import Discount

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['house', 'discount_percentage', 'start_date', 'end_date']
