from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST  # Добавьте эту строку
from datetime import datetime, timedelta
import json
from .models import Customer, Order, OrderStatus, PlannerSettings
from .forms import CustomerForm, OrderForm, OrderStatusForm, PlannerSettingsForm

def index(request):
    planner_settings = PlannerSettings.objects.first()
    if not planner_settings:
        planner_settings = PlannerSettings.objects.create()
    
    # Получаем заказы с планируемыми датами и сортируем по порядку в дне
    orders = Order.objects.filter(planned_date__isnull=False).order_by('planned_date', 'order_in_day')
    
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
            'day_percentage': min(day_percentage, 100)  # не более 100%
        })
    
    context = {
        'days': days_of_week,
        'planner_settings': planner_settings,
        'orders_without_date': Order.objects.filter(planned_date__isnull=True),
        'total_day_minutes': planner_settings.hours_per_day * 60  # общее количество минут в рабочем дне
    }
    return render(request, 'atelier/index.html', context)

@require_POST
def update_order_planning(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            planned_date = data.get('planned_date')
            order_in_day = data.get('order_in_day')  # новый параметр для порядка
            
            order = Order.objects.get(id=order_id)
            
            if planned_date:
                order.planned_date = planned_date
            
            if order_in_day is not None:
                order.order_in_day = order_in_day
            
            order.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

def order_status_list(request):
    statuses = OrderStatus.objects.all()
    return render(request, 'atelier/order_status_list.html', {'statuses': statuses})

def order_status_create(request):
    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            # Если устанавливается как статус по умолчанию, снимаем флаг с других
            if form.cleaned_data['is_default']:
                OrderStatus.objects.filter(is_default=True).update(is_default=False)
            form.save()
            return redirect('order_status_list')
    else:
        form = OrderStatusForm()
    return render(request, 'atelier/order_status_form.html', {'form': form})

def order_status_edit(request, pk):
    status = get_object_or_404(OrderStatus, pk=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=status)
        if form.is_valid():
            if form.cleaned_data['is_default']:
                OrderStatus.objects.filter(is_default=True).update(is_default=False)
            form.save()
            return redirect('order_status_list')
    else:
        form = OrderStatusForm(instance=status)
    return render(request, 'atelier/order_status_form.html', {'form': form})

def order_status_delete(request, pk):
    status = get_object_or_404(OrderStatus, pk=pk)
    if request.method == 'POST':
        status.delete()
        return redirect('order_status_list')
    return render(request, 'atelier/order_status_confirm_delete.html', {'status': status})

def planner_settings(request):
    settings = PlannerSettings.objects.first()
    if not settings:
        settings = PlannerSettings.objects.create()
    
    if request.method == 'POST':
        form = PlannerSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = PlannerSettingsForm(instance=settings)
    
    return render(request, 'atelier/planner_settings.html', {'form': form})

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'atelier/customer_list.html', {'customers': customers})

def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.all()
    return render(request, 'atelier/customer_detail.html', {
        'customer': customer,
        'orders': orders
    })

def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    return render(request, 'atelier/customer_form.html', {'form': form})

def customer_edit(request, pk):  # Параметр должен называться pk
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer.pk)  # Редирект после успеха
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'atelier/customer_form.html', {'form': form})

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'atelier/order_list.html', {'orders': orders})

def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'atelier/order_detail.html', {'order': order})

def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()
    return render(request, 'atelier/order_form.html', {'form': form})

def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
    return render(request, 'atelier/order_form.html', {'form': form})

@require_POST  # Теперь этот декоратор будет работать
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('customer_list')

@require_POST
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    return redirect('order_list')