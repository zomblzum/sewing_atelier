from django import forms
from .models import Customer, Order, OrderStatus, PlannerSettings

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'phone', 'comment']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['title', 'customer', 'price', 'comment', 'status', 
                 'planned_date', 'planned_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'planned_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planned_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = OrderStatus
        fields = ['name', 'color', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PlannerSettingsForm(forms.ModelForm):
    class Meta:
        model = PlannerSettings
        fields = ['hours_per_day', 'work_days']
        widgets = {
            'hours_per_day': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 24}),
            'work_days': forms.TextInput(attrs={'class': 'form-control'}),
        }