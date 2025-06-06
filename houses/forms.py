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
from .models import CleaningFeeSetting, CleaningFeePerHouse, House

class CleaningFeeForm(forms.ModelForm):
    class Meta:
        model = CleaningFeeSetting
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'class': 'form-control',
                'placeholder': 'e.g. 25.00',
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount < 0:
            raise forms.ValidationError("The cleaning fee cannot be negative.")
        return amount

class HouseCleaningFeeForm(forms.ModelForm):
    class Meta:
        model = CleaningFeePerHouse
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'class': 'form-control',
                'placeholder': 'e.g. 25.00',
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount < 0:
            raise forms.ValidationError("The cleaning fee cannot be negative.")
        return amount
