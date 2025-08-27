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
    customer_first_name = forms.CharField(
        max_length=100, 
        required=False, 
        label="Имя клиента",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите имя',
            'autocomplete': 'off',
            'id': 'id_customer_first_name'
        })
    )
    customer_phone = forms.CharField(
        max_length=17, 
        required=False, 
        label="Телефон клиента",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '+79991234567',
            'autocomplete': 'off',
            'id': 'id_customer_phone'
        })
    )
    
    class Meta:
        model = Order
        fields = ['title', 'category', 'price', 'comment', 'status', 
                 'planned_date', 'planned_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
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
            # Фильтруем категории и статусы только текущего пользователя
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
            self.fields['status'].queryset = OrderStatus.objects.filter(user=self.user)
        
        # Заполняем поля имени и телефона, если заказ уже существует
        if self.instance and self.instance.pk and self.instance.customer:
            self.initial['customer_first_name'] = self.instance.customer.first_name
            self.initial['customer_phone'] = self.instance.customer.phone
    
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('customer_first_name')
        phone = cleaned_data.get('customer_phone')
        
        # Валидация обязательных полей
        if not first_name:
            self.add_error('customer_first_name', 'Обязательное поле')
        if not phone:
            self.add_error('customer_phone', 'Обязательное поле')
        
        return cleaned_data
    
    def save(self, commit=True):
        order = super().save(commit=False)
        first_name = self.cleaned_data['customer_first_name']
        phone = self.cleaned_data['customer_phone']
        
        # Ищем существующего клиента или создаем нового
        try:
            customer = Customer.objects.get(user=self.user, phone=phone)
            # Обновляем имя, если клиент уже существовал
            customer.first_name = first_name
            customer.save()
        except Customer.DoesNotExist:
            # Создаем нового клиента
            customer = Customer.objects.create(
                user=self.user,
                first_name=first_name,
                last_name='',  # Можно добавить логику для фамилии если нужно
                phone=phone
            )
        
        order.customer = customer
        order.user = self.user  # Убедимся, что пользователь установлен
        
        if commit:
            order.save()
        
        return order

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