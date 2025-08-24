from django import forms
from .models import Customer, Order, OrderStatus, PlannerSettings, Category

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

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'default_price', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название категории'
            }),
            'default_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
        }
        labels = {
            'name': 'Название категории',
            'default_price': 'Цена по умолчанию',
            'color': 'Цвет'
        }
        help_texts = {
            'default_price': 'Цена в рублях',
            'color': 'Выберите цвет для визуального отличия'
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
        super().__init__(*args, **kwargs)
        # Устанавливаем подсказку для поля planned_minutes
        self.fields['planned_minutes'].help_text = 'Продолжительность заказа в минутах'
        if self.instance and self.instance.pk:
            print(f"Editing order {self.instance.pk}, planned_date: {self.instance.planned_date}")        

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