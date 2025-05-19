from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('create/', views.order_create, name='order_create'),
    path('order-complete/<int:order_id>/', views.order_complete, name='order_complete'),
    path('order-history/', views.order_history, name='order_history'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order-cancel/<int:order_id>/', views.order_cancel, name='cancel_order'),
] 