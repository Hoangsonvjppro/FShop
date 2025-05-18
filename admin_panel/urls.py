from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    
    # Sản phẩm
    path('products/', views.product_list, name='admin_product_list'),
    path('products/add/', views.product_add, name='admin_product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='admin_product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='admin_product_delete'),
    
    # Danh mục
    path('categories/', views.category_list, name='admin_category_list'),
    path('categories/add/', views.category_add, name='admin_category_add'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='admin_category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='admin_category_delete'),
    
    # Thương hiệu
    path('brands/', views.brand_list, name='admin_brand_list'),
    path('brands/add/', views.brand_add, name='admin_brand_add'),
    path('brands/<int:brand_id>/edit/', views.brand_edit, name='admin_brand_edit'),
    path('brands/<int:brand_id>/delete/', views.brand_delete, name='admin_brand_delete'),
    
    # Đơn hàng
    path('orders/', views.order_list, name='admin_order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='admin_order_detail'),
    path('orders/<int:order_id>/update-status/', views.order_update_status, name='admin_order_update_status'),
    
    # Khách hàng
    path('customers/', views.customer_list, name='admin_customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='admin_customer_detail'),
    path('customers/<int:customer_id>/toggle-status/', views.customer_toggle_status, name='admin_customer_toggle_status'),
    
    # Nhân viên
    path('employees/', views.employee_list, name='admin_employee_list'),
    path('employees/add/', views.employee_add, name='admin_employee_add'),
    path('employees/<int:employee_id>/edit/', views.employee_edit, name='admin_employee_edit'),
    path('employees/<int:employee_id>/delete/', views.employee_delete, name='admin_employee_delete'),
    
    # Vai trò và phân quyền
    path('roles/', views.role_list, name='admin_role_list'),
    path('roles/add/', views.role_add, name='admin_role_add'),
    path('roles/<int:role_id>/edit/', views.role_edit, name='admin_role_edit'),
    path('roles/<int:role_id>/delete/', views.role_delete, name='admin_role_delete'),
    
    # Nhập hàng
    path('imports/', views.import_list, name='admin_import_list'),
    path('imports/add/', views.import_add, name='admin_import_add'),
    path('imports/<int:import_id>/', views.import_detail, name='admin_import_detail'),
    
    # Nhà cung cấp
    path('suppliers/', views.supplier_list, name='admin_supplier_list'),
    path('suppliers/add/', views.supplier_add, name='admin_supplier_add'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='admin_supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', views.supplier_delete, name='admin_supplier_delete'),
    
    # Thống kê
    path('statistics/', views.statistics, name='admin_statistics'),
    path('statistics/products/', views.product_statistics, name='admin_product_statistics'),
    path('statistics/customers/', views.customer_statistics, name='admin_customer_statistics'),
    path('statistics/sales/', views.sales_statistics, name='admin_sales_statistics'),
    
    # Báo cáo
    path('reports/', views.admin_reports, name='admin_reports'),
    
    # Cài đặt
    path('settings/', views.admin_settings, name='admin_settings'),
    
    # Tài khoản
    path('profile/', views.admin_settings, name='admin_profile'),
] 