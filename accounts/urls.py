from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/addresses/', views.address_list, name='address_list'),
    path('profile/addresses/add/', views.address_add, name='address_add'),
    path('profile/addresses/<int:address_id>/edit/', views.address_edit, name='address_edit'),
    path('profile/addresses/<int:address_id>/delete/', views.address_delete, name='address_delete'),
] 