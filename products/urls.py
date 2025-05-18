from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.product_list, name='product_list'),
    path('shop/category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('shop/brand/<slug:brand_slug>/', views.product_list, name='product_list_by_brand'),
    path('shop/room/<str:room_type>/', views.product_list, name='product_list_by_room'),
    path('shop/material/<str:material>/', views.product_list, name='product_list_by_material'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
] 