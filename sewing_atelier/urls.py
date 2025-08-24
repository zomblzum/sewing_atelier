from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from atelier import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('atelier.urls')),  # Важно!
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('orders/', views.order_list, name='order_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('orders/new/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'), 
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)