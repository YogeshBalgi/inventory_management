"""
URL configuration for kamakshi_auto_care project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mykac import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('stock/', views.stock, name='stock'),
    path('order/', views.order, name='order'),
    path('update_stock/', views.update_stock, name='update_stock'),
    path('delete_stock/', views.delete_stock, name='delete_stock'),
    path('update_order/', views.update_order, name='update_order'),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('send_order_email/<int:vendor_id>/', views.send_order_email, name='send_order_email'),
    path('vendors/', views.vendors, name='vendors'),
    path('vendor/update/<int:vendor_id>/', views.update_vendor, name='update_vendor'),
    path('vendor/delete/<int:vendor_id>/', views.delete_vendor, name='delete_vendor'),
    path('admin/', admin.site.urls),
]
