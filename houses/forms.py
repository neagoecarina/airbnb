from django import forms
from .models import Discount

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['house', 'discount_percentage', 'start_date', 'end_date']

from django import forms
from .models import Booking



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['customer_name', 'house', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

from django import forms
from .models import CleaningFeeSetting

class CleaningFeeForm(forms.ModelForm):
    class Meta:
        model = CleaningFeeSetting
        fields = ['amount']
