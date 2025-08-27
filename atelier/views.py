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
from django.template.loader import render_to_string

# Auth views
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Создаем дефолтные настройки
                PlannerSettings.objects.create(user=user)
                
                # Создаем дефолтные статусы
                default_statuses = [
                    {'name': 'Новый', 'color': '#007bff', 'is_default': True},
                    {'name': 'В работе', 'color': '#28a745', 'is_default': False},
                    {'name': 'Завершен', 'color': "#ffffff", 'is_default': False},
                    {'name': 'Отменен', 'color': '#6c757d', 'is_default': False}
                ]
                
                for status_data in default_statuses:
                    OrderStatus.objects.create(user=user, **status_data)
                
                login(request, user)
                return redirect('index')
                
            except Exception as e:
                # Логируем ошибку и показываем пользователю
                form.add_error(None, f'Ошибка при создании пользователя: {str(e)}')
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
    # Получаем начальную дату из параметра или используем текущую
    start_date_str = request.GET.get('start_date')
    if start_date_str:
        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            # Если передан некорректный формат даты, используем текущую неделю
            start_date = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
    else:
        start_date = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
    
    # Получаем количество недель или используем 1 по умолчанию
    weeks_str = request.GET.get('weeks')
    if weeks_str:
        try:
            weeks_to_show = max(1, int(weeks_str))  # Минимум 1 неделя
        except ValueError:
            weeks_to_show = 1
    else:
        weeks_to_show = 1
    
    planner_settings, created = PlannerSettings.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user, planned_date__isnull=False).order_by('planned_date', 'order_in_day')
    
    # Генерируем дни для отображения (недели)
    days_of_week = []
    total_days = 7 * weeks_to_show
    
    if planner_settings.work_days.strip():
        work_days = list(map(int, planner_settings.work_days.split(',')))
    else:
        work_days = [1, 2, 3, 4, 5]
    
    for i in range(total_days):
        day_date = start_date + timedelta(days=i)
        day_orders = orders.filter(planned_date=day_date)
        
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
        'total_day_minutes': planner_settings.hours_per_day * 60,
        'start_date': start_date,
        'weeks': weeks_to_show,
        'end_date': start_date + timedelta(days=7 * weeks_to_show - 1),
    }
    return render(request, 'atelier/index.html', context)

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
    # Получаем дату из параметра URL
    planned_date_str = request.GET.get('planned_date')
    
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            
            # Сохраняем planned_date из формы (может быть переопределен пользователем)
            if form.cleaned_data.get('planned_date'):
                order.planned_date = form.cleaned_data['planned_date']
            
            order.save()
            return redirect('index')
    else:
        # Создаем форму с начальными значениями
        initial = {}
        if planned_date_str:
            try:
                planned_date = timezone.datetime.strptime(planned_date_str, '%Y-%m-%d').date()
                initial['planned_date'] = planned_date
            except ValueError:
                pass
        
        form = OrderForm(user=request.user, initial=initial)
    
    return render(request, 'atelier/order_form.html', {'form': form})

@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            order = form.save()
            return redirect('index')
    else:
        form = OrderForm(instance=order, user=request.user)
    return render(request, 'atelier/order_form.html', {'form': form})

@login_required
@require_POST
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    order.delete()
    return redirect('order_list')

@login_required
def get_category_price(request, pk):
    try:
        category = Category.objects.get(pk=pk, user=request.user)
        return JsonResponse({'price': float(category.default_price)})
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    
@login_required
@require_POST
def check_day_limit(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        planned_date = data.get('planned_date')
        
        # Добавляем проверку пользователя
        order = get_object_or_404(Order, id=order_id, user=request.user)
        planner_settings = get_object_or_404(PlannerSettings, user=request.user)
        
        if planned_date:
            day_orders = Order.objects.filter(planned_date=planned_date, user=request.user)
            total_minutes = sum(o.planned_minutes for o in day_orders if o.planned_minutes)
            
            if order.planned_date == planned_date:
                total_minutes -= order.planned_minutes or 0
            
            total_minutes += order.planned_minutes or 0
            
            day_minutes_limit = planner_settings.hours_per_day * 60
            can_add = total_minutes <= day_minutes_limit
            
            return JsonResponse({
                'can_add': can_add,
                'total_minutes': total_minutes,
                'limit': day_minutes_limit
            })
        
        return JsonResponse({'can_add': True})
    except Exception as e:
        return JsonResponse({'can_add': True, 'error': str(e)})
    
@login_required
def customer_list_json(request):
    customers = Customer.objects.filter(user=request.user).values('id', 'first_name', 'phone')
    return JsonResponse(list(customers), safe=False)    

def split_order_to_days(order, target_date):
    """Дробит заказ на дни"""
    if not order.is_main_part:
        # Если это часть заказа, работаем с основным заказом
        order = order.parent_order
    
    planner_settings = PlannerSettings.objects.get(user=order.user)
    day_minutes = planner_settings.hours_per_day * 60
    
    # Удаляем существующие части
    Order.objects.filter(parent_order=order).delete()
    
    remaining_minutes = order.planned_minutes
    current_date = target_date
    part_number = 1
    
    # Распределяем минуты по дням
    while remaining_minutes > 0:
        # Получаем или создаем часть заказа
        if part_number == 1:
            order_part = order
            order_part.planned_date = current_date
            order_part.part_number = 1
        else:
            order_part = Order.objects.create(
                user=order.user,
                title=f"{order.title} (ч.{part_number})",
                customer=order.customer,
                category=order.category,
                price=order.price / order.total_parts if order.total_parts > 1 else order.price,
                comment=order.comment,
                status=order.status,
                planned_date=current_date,
                planned_minutes=0,
                color=order.color,
                parent_order=order,
                is_main_part=False,
                part_number=part_number
            )
        
        # Рассчитываем доступное время в текущем дне
        existing_orders = Order.objects.filter(
            user=order.user,
            planned_date=current_date,
            parent_order__isnull=True  # Учитываем только основные заказы
        ).exclude(id=order_part.id)
        
        used_minutes = sum(o.planned_minutes for o in existing_orders)
        available_minutes = max(0, day_minutes - used_minutes)
        
        # Распределяем минуты
        minutes_for_day = min(remaining_minutes, available_minutes)
        order_part.planned_minutes = minutes_for_day
        order_part.save()
        
        remaining_minutes -= minutes_for_day
        current_date += timedelta(days=1)
        part_number += 1
    
    # Обновляем общее количество частей
    order.total_parts = part_number - 1
    order.save()
    
    return order.get_all_parts()

@login_required
@require_POST
def update_order_planning(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        planned_date = data.get('planned_date')
        order_in_day = data.get('order_in_day')
        
        # Получаем параметры с проверкой на None
        start_date_str = data.get('start_date')
        weeks_str = data.get('weeks', '1')
        
        # Обработка параметров как в index view
        if start_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
        else:
            start_date = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
        
        try:
            weeks = max(1, int(weeks_str))
        except (ValueError, TypeError):
            weeks = 1
        
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        if planned_date:
            # Если заказ многодневный - используем функцию с дроблением
            if order.planned_minutes > 0 and order.is_main_part:
                update_order_planning_with_splitting(order, planned_date, order_in_day, request.user)
            else:
                # Простое перемещение для частей заказов или обычных заказов
                order.planned_date = planned_date
                
                # Исправляем обработку order_in_day
                if order_in_day is not None and order_in_day != '':
                    try:
                        order.order_in_day = int(order_in_day)
                    except (ValueError, TypeError):
                        order.order_in_day = None
                else:
                    order.order_in_day = None
                
                order.save()
        else:
            # Перемещение в "без даты" - удаляем все части если это основной заказ
            if order.is_main_part:
                Order.objects.filter(parent_order=order).delete()
            order.planned_date = None
            order.order_in_day = None
            order.save()
        
        # Если это AJAX-запрос, возвращаем HTML всего планера
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            planner_settings = PlannerSettings.objects.get(user=request.user)
            
            # Получаем заказы, учитывая многодневные части
            orders = Order.objects.filter(
                user=request.user, 
                planned_date__isnull=False
            ).exclude(
                is_main_part=False  # Исключаем части, показываем только основные
            ).order_by('planned_date', 'order_in_day')
            
            days_of_week = []
            total_days = 7 * weeks
            
            if planner_settings.work_days.strip():
                work_days = list(map(int, planner_settings.work_days.split(',')))
            else:
                work_days = [1, 2, 3, 4, 5]
            
            for i in range(total_days):
                day_date = start_date + timedelta(days=i)
                
                # Получаем все заказы для дня (включая части многодневных)
                day_orders = Order.objects.filter(
                    user=request.user,
                    planned_date=day_date
                )
                
                total_minutes = sum(order.planned_minutes for order in day_orders)
                day_percentage = (total_minutes / (planner_settings.hours_per_day * 60)) * 100
                
                # Получаем только основные заказы для отображения
                main_orders = day_orders.filter(
                    Q(is_main_part=True) | Q(parent_order__isnull=True)
                )
                
                days_of_week.append({
                    'date': day_date,
                    'orders': main_orders,
                    'is_work_day': (day_date.weekday() + 1) in work_days,
                    'total_minutes': total_minutes,
                    'day_percentage': min(day_percentage, 100),
                    'is_over_limit': total_minutes > (planner_settings.hours_per_day * 60),
                    'over_minutes': max(0, total_minutes - (planner_settings.hours_per_day * 60))
                })
            
            # Получаем заказы без даты (только основные)
            orders_without_date = Order.objects.filter(
                user=request.user, 
                planned_date__isnull=True
            ).exclude(is_main_part=False)
            
            html = render_to_string('atelier/index.html', {
                'days': days_of_week,
                'planner_settings': planner_settings,
                'orders_without_date': orders_without_date,
                'total_day_minutes': planner_settings.hours_per_day * 60,
                'start_date': start_date,
                'weeks': weeks
            }, request=request)
            
            return JsonResponse({'success': True, 'html': html})
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        print(f"Error in update_order_planning: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


def update_order_planning_with_splitting(order, target_date, order_in_day, user):
    """Обновляет планирование с учетом дробления многодневных заказов"""
    try:
        planner_settings = PlannerSettings.objects.get(user=user)
        day_minutes = planner_settings.hours_per_day * 60
        
        # Удаляем существующие части
        Order.objects.filter(parent_order=order).delete()
        
        remaining_minutes = order.planned_minutes
        current_date = target_date
        part_number = 1
        
        # Распределяем минуты по дням
        while remaining_minutes > 0:
            # Получаем доступное время в текущем дне
            existing_orders = Order.objects.filter(
                user=user,
                planned_date=current_date
            ).exclude(id=order.id)
            
            used_minutes = sum(o.planned_minutes for o in existing_orders)
            available_minutes = max(0, day_minutes - used_minutes)
            
            if available_minutes <= 0:
                # Переходим к следующему дню
                current_date += timedelta(days=1)
                continue
            
            # Распределяем минуты
            minutes_for_day = min(remaining_minutes, available_minutes)
            
            if part_number == 1:
                # Основная часть
                order.planned_date = current_date
                order.planned_minutes = minutes_for_day
                order.order_in_day = order_in_day
                order.part_number = 1
                order.save()
            else:
                # Дополнительная часть
                Order.objects.create(
                    user=user,
                    title=f"{order.title} (ч.{part_number})",
                    customer=order.customer,
                    category=order.category,
                    price=order.price,
                    comment=order.comment,
                    status=order.status,
                    planned_date=current_date,
                    planned_minutes=minutes_for_day,
                    color=order.color,
                    parent_order=order,
                    is_main_part=False,
                    part_number=part_number
                )
            
            remaining_minutes -= minutes_for_day
            current_date += timedelta(days=1)
            part_number += 1
        
        # Обновляем общее количество частей
        order.total_parts = part_number - 1
        order.save()
        
        # Перераспределяем порядок в affected days
        redistribute_affected_days(order, target_date, user)
        
    except Exception as e:
        print(f"Error in update_order_planning_with_splitting: {str(e)}")
        raise


def redistribute_affected_days(main_order, start_date, user):
    """Перераспределяет заказы в affected days после изменений"""
    try:
        all_parts = main_order.get_all_parts()
        affected_dates = list(set(
            part.planned_date for part in all_parts if part.planned_date
        ))
        
        for date in affected_dates:
            # Пересчитываем порядок заказов в дне
            orders = Order.objects.filter(
                user=user,
                planned_date=date
            ).order_by('order_in_day', 'created_at')
            
            current_order = 0
            for order in orders:
                order.order_in_day = current_order
                order.save()
                current_order += 1
            
            # Проверяем переполнение
            check_and_split_overflows(date, user)
            
    except Exception as e:
        print(f"Error in redistribute_affected_days: {str(e)}")
        raise


def check_and_split_overflows(date, user):
    """Проверяет переполнение дней и дробит заказы при необходимости"""
    try:
        planner_settings = PlannerSettings.objects.get(user=user)
        day_minutes = planner_settings.hours_per_day * 60
        
        orders = Order.objects.filter(user=user, planned_date=date)
        total_minutes = sum(order.planned_minutes for order in orders)
        
        if total_minutes > day_minutes:
            # Находим самый большой заказ для дробления
            largest_order = orders.filter(is_main_part=True).order_by('-planned_minutes').first()
            if largest_order and largest_order.planned_minutes > 30:
                update_order_planning_with_splitting(
                    largest_order, 
                    date, 
                    largest_order.order_in_day, 
                    user
                )
                
    except Exception as e:
        print(f"Error in check_and_split_overflows: {str(e)}")