from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('order-complete/<int:order_id>/', views.order_complete, name='order_complete'),
    path('order-history/', views.order_history, name='order_history'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
] 