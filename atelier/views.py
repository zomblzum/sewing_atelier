from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Order
from .forms import CustomerForm, OrderForm
from django.views.decorators.http import require_POST
from django.contrib import messages


def index(request):
    return render(request, 'atelier/index.html')  # или перенаправьте на другую страницу

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

@require_POST  # Защита от случайного удаления через GET-запрос
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    messages.success(request, 'Клиент успешно удалён')
    return redirect('customer_list')

@require_POST
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    messages.success(request, 'Заказ успешно удалён')
    return redirect('order_list')