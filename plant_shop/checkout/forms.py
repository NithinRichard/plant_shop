from django import forms
from .models import Order, ShippingAddress

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'state', 'postal_code', 'country',
            'shipping_method', 'payment_method'
        ]
        widgets = {
            'shipping_method': forms.RadioSelect(),
            'payment_method': forms.RadioSelect()
        }

class AddressForm(forms.ModelForm):
    is_default = forms.BooleanField(
        required=False,
        initial=False,
        label='Set as default address'
    )
    
    class Meta:
        model = ShippingAddress
        fields = [
            'name', 'phone', 'address', 'city', 
            'state', 'postal_code', 'country', 'is_default'
        ]