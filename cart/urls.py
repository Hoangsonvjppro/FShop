from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('clear/', views.cart_clear, name='cart_clear'),
    path('saved-items/', views.saved_items, name='saved_items'),
    path('save/<int:product_id>/', views.save_item, name='save_item'),
    path('unsave/<int:product_id>/', views.unsave_item, name='unsave_item'),
] 