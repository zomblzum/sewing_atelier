from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('update_order_planning/', views.update_order_planning, name='update_order_planning'),
    path('order_statuses/', views.order_status_list, name='order_status_list'),
    path('order_statuses/new/', views.order_status_create, name='order_status_create'),
    path('order_statuses/<int:pk>/edit/', views.order_status_edit, name='order_status_edit'),
    path('order_statuses/<int:pk>/delete/', views.order_status_delete, name='order_status_delete'),
    path('planner_settings/', views.planner_settings, name='planner_settings'),
    
    # Существующие URL
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),    

    path('api/category/<int:pk>/price/', views.get_category_price, name='category_price'),
]