from django import forms
from .models import Product, Cart

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price']

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['products']
