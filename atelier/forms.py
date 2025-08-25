from django import forms
from .models import Customer, Order, OrderStatus, PlannerSettings, Category
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

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
        fields = ['title', 'customer', 'category', 'price', 'comment', 'status', 
                 'planned_date', 'planned_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_price'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'planned_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'id': 'id_planned_date'
            }),
            'planned_minutes': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1,
                'placeholder': 'Введите время в минутах'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Фильтруем клиентов, категории и статусы только текущего пользователя
            self.fields['customer'].queryset = Customer.objects.filter(user=self.user)
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
            self.fields['status'].queryset = OrderStatus.objects.filter(user=self.user)

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = OrderStatus
        fields = ['name', 'color', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'default_price', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'default_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

class PlannerSettingsForm(forms.ModelForm):
    class Meta:
        model = PlannerSettings
        fields = ['hours_per_day', 'work_days']
        widgets = {
            'hours_per_day': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 24}),
            'work_days': forms.TextInput(attrs={'class': 'form-control'}),
        }