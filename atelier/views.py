from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json
from .models import Customer, Order, OrderStatus, PlannerSettings, Category
from .forms import CustomerForm, OrderForm, OrderStatusForm, PlannerSettingsForm, CategoryForm, RegisterForm, LoginForm

# Auth views
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Создаем дефолтные настройки для нового пользователя
            PlannerSettings.objects.create(user=user)
            
            # Создаем дефолтные статусы
            default_statuses = [
                {'name': 'Новый', 'color': '#007bff', 'is_default': True},
                {'name': 'В работе', 'color': '#28a745', 'is_default': False},
                {'name': 'Завершен', 'color': '#6c757d', 'is_default': False},
                {'name': 'Отменен', 'color': '#dc3545', 'is_default': False}
            ]
            
            for status_data in default_statuses:
                OrderStatus.objects.create(user=user, **status_data)
            
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    
    return render(request, 'atelier/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = LoginForm()
    
    return render(request, 'atelier/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Main views with user isolation
@login_required
def index(request):
    # Получаем настройки планера для текущего пользователя
    planner_settings, created = PlannerSettings.objects.get_or_create(user=request.user)
    
    # Получаем заказы с планируемыми датами текущего пользователя
    orders = Order.objects.filter(user=request.user, planned_date__isnull=False).order_by('planned_date', 'order_in_day')
    
    # Генерируем дни для отображения (текущая неделя)
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    days_of_week = []
    
    work_days = list(map(int, planner_settings.work_days.split(',')))
    
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        day_orders = orders.filter(planned_date=day_date)
        
        # Рассчитываем общую занятость дня в минутах
        total_minutes = sum(order.planned_minutes for order in day_orders)
        day_percentage = (total_minutes / (planner_settings.hours_per_day * 60)) * 100
        
        days_of_week.append({
            'date': day_date,
            'orders': day_orders,
            'is_work_day': (day_date.weekday() + 1) in work_days,
            'total_minutes': total_minutes,
            'day_percentage': min(day_percentage, 100)
        })
    
    context = {
        'days': days_of_week,
        'planner_settings': planner_settings,
        'orders_without_date': Order.objects.filter(user=request.user, planned_date__isnull=True),
        'total_day_minutes': planner_settings.hours_per_day * 60
    }
    return render(request, 'atelier/index.html', context)

@login_required
@require_POST
def update_order_planning(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            planned_date = data.get('planned_date')
            order_in_day = data.get('order_in_day')
            
            # Проверяем, что заказ принадлежит текущему пользователю
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            if planned_date:
                order.planned_date = planned_date
            else:
                order.planned_date = None
            
            if order_in_day is not None:
                order.order_in_day = order_in_day
            else:
                order.order_in_day = None
            
            order.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

# Order Status views
@login_required
def order_status_list(request):
    statuses = OrderStatus.objects.filter(user=request.user)
    return render(request, 'atelier/order_status_list.html', {'statuses': statuses})

@login_required
def order_status_create(request):
    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.user = request.user
            
            # Если устанавливается как статус по умолчанию, снимаем флаг с других
            if form.cleaned_data['is_default']:
                OrderStatus.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            status.save()
            return redirect('order_status_list')
    else:
        form = OrderStatusForm()
    return render(request, 'atelier/order_status_form.html', {'form': form})

@login_required
def order_status_edit(request, pk):
    status = get_object_or_404(OrderStatus, pk=pk, user=request.user)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=status)
        if form.is_valid():
            if form.cleaned_data['is_default']:
                OrderStatus.objects.filter(user=request.user, is_default=True).update(is_default=False)
            form.save()
            return redirect('order_status_list')
    else:
        form = OrderStatusForm(instance=status)
    return render(request, 'atelier/order_status_form.html', {'form': form})

@login_required
def order_status_delete(request, pk):
    status = get_object_or_404(OrderStatus, pk=pk, user=request.user)
    if request.method == 'POST':
        status.delete()
        return redirect('order_status_list')
    return render(request, 'atelier/order_status_confirm_delete.html', {'status': status})

# Category views
@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'atelier/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'atelier/category_form.html', {'form': form})

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'atelier/category_form.html', {'form': form})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'atelier/category_confirm_delete.html', {'category': category})

# Planner Settings views
@login_required
def planner_settings(request):
    settings, created = PlannerSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = PlannerSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = PlannerSettingsForm(instance=settings)
    
    return render(request, 'atelier/planner_settings.html', {'form': form})

# Customer views
@login_required
def customer_list(request):
    customers = Customer.objects.filter(user=request.user)
    return render(request, 'atelier/customer_list.html', {'customers': customers})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    orders = customer.orders.filter(user=request.user)
    return render(request, 'atelier/customer_detail.html', {
        'customer': customer,
        'orders': orders
    })

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    return render(request, 'atelier/customer_form.html', {'form': form})

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'atelier/customer_form.html', {'form': form})

@login_required
@require_POST
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)
    customer.delete()
    return redirect('customer_list')

# Order views
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'atelier/order_list.html', {'orders': orders})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'atelier/order_detail.html', {'order': order})

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(user=request.user)
    return render(request, 'atelier/order_form.html', {'form': form})

@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            order = form.save()
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order, user=request.user)
    return render(request, 'atelier/order_form.html', {'form': form})

@login_required
@require_POST
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    order.delete()
    return redirect('order_list')

def get_category_price(request, pk):
    try:
        category = Category.objects.get(pk=pk)
        return JsonResponse({'price': float(category.default_price)})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)