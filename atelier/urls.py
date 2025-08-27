from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Auth URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main URLs
    path('', views.index, name='index'),
    path('update-order-planning/', views.update_order_planning, name='update_order_planning'),
    
    # Order Status URLs
    path('order-statuses/', views.order_status_list, name='order_status_list'),
    path('order-statuses/create/', views.order_status_create, name='order_status_create'),
    path('order-statuses/<int:pk>/edit/', views.order_status_edit, name='order_status_edit'),
    path('order-statuses/<int:pk>/delete/', views.order_status_delete, name='order_status_delete'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Planner Settings URLs
    path('settings/', views.planner_settings, name='planner_settings'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Order URLs
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'), 

    path('api/category/<int:pk>/price/', views.get_category_price, name='category_price'),
    path('check-day-limit/', views.check_day_limit, name='check_day_limit'),

    path('customers/json/', views.customer_list_json, name='customer_list_json'),    
]