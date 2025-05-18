from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from accounts.models import Customer, Employee, Role, Permission
from products.models import Product, Category, Brand, ProductImage, Supplier, Import, ImportDetail
from orders.models import Order, OrderItem
from django.contrib.auth.models import User


def is_admin(user):
    """Kiểm tra người dùng có quyền admin."""
    try:
        return user.is_authenticated and hasattr(user, 'employee') and user.employee.role is not None
    except:
        return False


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Trang tổng quan admin."""
    # Thống kê cơ bản
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status__in=['completed', 'delivered']).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Tính % tăng/giảm so với tháng trước
    current_month = timezone.now()
    last_month = current_month - timedelta(days=30)
    
    # Đơn hàng tháng này vs tháng trước
    orders_current_month = Order.objects.filter(created_at__gte=last_month).count()
    orders_last_month = Order.objects.filter(created_at__lt=last_month, created_at__gte=last_month - timedelta(days=30)).count()
    order_percent_increase = calculate_percent_change(orders_current_month, orders_last_month)
    
    # Doanh thu tháng này vs tháng trước
    revenue_current_month = Order.objects.filter(created_at__gte=last_month, status__in=['completed', 'delivered']).aggregate(Sum('total_price'))['total_price__sum'] or 0
    revenue_last_month = Order.objects.filter(created_at__lt=last_month, created_at__gte=last_month - timedelta(days=30), status__in=['completed', 'delivered']).aggregate(Sum('total_price'))['total_price__sum'] or 0
    revenue_percent_increase = calculate_percent_change(revenue_current_month, revenue_last_month)
    
    # Khách hàng mới tháng này vs tháng trước
    customers_current_month = Customer.objects.filter(created_at__gte=last_month).count()
    customers_last_month = Customer.objects.filter(created_at__lt=last_month, created_at__gte=last_month - timedelta(days=30)).count()
    customer_percent_increase = calculate_percent_change(customers_current_month, customers_last_month)
    
    # Sản phẩm mới tháng này vs tháng trước
    products_current_month = Product.objects.filter(created_at__gte=last_month).count()
    products_last_month = Product.objects.filter(created_at__lt=last_month, created_at__gte=last_month - timedelta(days=30)).count()
    product_percent_increase = calculate_percent_change(products_current_month, products_last_month)
    
    # Sản phẩm sắp hết hàng
    low_stock_products = Product.objects.filter(stock__lte=5, available=True, is_deleted=False).order_by('stock')[:5]
    
    # Đơn hàng gần đây
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'order_percent_increase': order_percent_increase,
        'revenue_percent_increase': revenue_percent_increase,
        'customer_percent_increase': customer_percent_increase,
        'product_percent_increase': product_percent_increase,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'admin_panel/simple_dashboard/dashboard.html', context)


def calculate_percent_change(current, previous):
    """Tính phần trăm thay đổi."""
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 2)


# PRODUCT MANAGEMENT
@login_required
@user_passes_test(is_admin)
def product_list(request):
    """Danh sách sản phẩm."""
    products = Product.objects.all()
    
    # Lọc sản phẩm
    filter_option = request.GET.get('filter', '')
    if filter_option == 'available':
        products = products.filter(available=True, is_deleted=False)
    elif filter_option == 'out_of_stock':
        products = products.filter(stock=0, is_deleted=False)
    elif filter_option == 'low_stock':
        products = products.filter(stock__lte=5, stock__gt=0, is_deleted=False)
    elif filter_option == 'deleted':
        products = products.filter(is_deleted=True)
    
    # Tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    context = {
        'products': products,
        'filter': filter_option,
        'search_query': search_query,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    
    return render(request, 'admin_panel/product_list.html', context)


@login_required
@user_passes_test(is_admin)
def product_add(request):
    """Thêm sản phẩm mới."""
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        room_type = request.POST.get('room_type')
        material = request.POST.get('material')
        dimensions = request.POST.get('dimensions')
        weight = request.POST.get('weight')
        warranty = request.POST.get('warranty')
        
        # Tạo sản phẩm mới
        product = Product.objects.create(
            name=name,
            slug=slug,
            category_id=category_id,
            brand_id=brand_id,
            description=description,
            price=price,
            stock=stock,
            room_type=room_type,
            material=material,
            dimensions=dimensions,
            weight=weight,
            warranty=warranty
        )
        
        # Xử lý nhiều ảnh sản phẩm
        images = request.FILES.getlist('images')
        for index, image in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_main=index == 0  # Ảnh đầu tiên là ảnh chính
            )
        
        messages.success(request, f'Đã thêm sản phẩm "{name}" thành công')
        return redirect('admin_product_list')
    
    context = {
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'room_types': Product.ROOM_CHOICES,
        'material_choices': Product.MATERIAL_CHOICES,
    }
    
    return render(request, 'admin_panel/product_add.html', context)


@login_required
@user_passes_test(is_admin)
def product_edit(request, product_id):
    """Chỉnh sửa sản phẩm."""
    product = get_object_or_404(Product, id=product_id)
    product_images = ProductImage.objects.filter(product=product)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.slug = request.POST.get('slug')
        product.category_id = request.POST.get('category')
        product.brand_id = request.POST.get('brand')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.room_type = request.POST.get('room_type')
        product.material = request.POST.get('material')
        product.dimensions = request.POST.get('dimensions')
        product.weight = request.POST.get('weight')
        product.warranty = request.POST.get('warranty')
        product.available = 'available' in request.POST
        product.is_deleted = 'is_deleted' in request.POST
        product.save()
        
        # Xử lý xóa ảnh
        if 'delete_images' in request.POST:
            image_ids = request.POST.getlist('delete_images')
            ProductImage.objects.filter(id__in=image_ids).delete()
        
        # Xử lý thêm ảnh mới
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(
                product=product,
                image=image,
                is_main=False
            )
        
        # Cập nhật ảnh chính
        main_image_id = request.POST.get('main_image')
        if main_image_id:
            ProductImage.objects.filter(product=product).update(is_main=False)
            ProductImage.objects.filter(id=main_image_id).update(is_main=True)
        
        messages.success(request, f'Đã cập nhật sản phẩm "{product.name}" thành công')
        return redirect('admin_product_list')
    
    context = {
        'product': product,
        'product_images': product_images,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'room_types': Product.ROOM_CHOICES,
        'material_choices': Product.MATERIAL_CHOICES,
    }
    
    return render(request, 'admin_panel/product_edit.html', context)


@login_required
@user_passes_test(is_admin)
def product_delete(request, product_id):
    """Xóa sản phẩm."""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Soft delete
        product.is_deleted = True
        product.available = False
        product.save()
        
        messages.success(request, f'Đã xóa sản phẩm "{product.name}" thành công')
        return redirect('admin_product_list')
    
    context = {
        'product': product,
    }
    
    return render(request, 'admin_panel/product_delete.html', context)


# CATEGORY MANAGEMENT
@login_required
@user_passes_test(is_admin)
def category_list(request):
    """Danh sách danh mục."""
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'admin_panel/category_list.html', context)


@login_required
@user_passes_test(is_admin)
def category_add(request):
    """Thêm danh mục mới."""
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        
        Category.objects.create(
            name=name,
            slug=slug
        )
        
        messages.success(request, f'Đã thêm danh mục "{name}" thành công')
        return redirect('admin_category_list')
    
    return render(request, 'admin_panel/category_add.html')


@login_required
@user_passes_test(is_admin)
def category_edit(request, category_id):
    """Chỉnh sửa danh mục."""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        category.save()
        
        messages.success(request, f'Đã cập nhật danh mục "{category.name}" thành công')
        return redirect('admin_category_list')
    
    context = {
        'category': category,
    }
    
    return render(request, 'admin_panel/category_edit.html', context)


@login_required
@user_passes_test(is_admin)
def category_delete(request, category_id):
    """Xóa danh mục."""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        
        messages.success(request, f'Đã xóa danh mục "{category_name}" thành công')
        return redirect('admin_category_list')
    
    context = {
        'category': category,
        'products_count': Product.objects.filter(category=category).count(),
    }
    
    return render(request, 'admin_panel/category_delete.html', context)


# BRAND MANAGEMENT
@login_required
@user_passes_test(is_admin)
def brand_list(request):
    """Danh sách thương hiệu."""
    brands = Brand.objects.all()
    
    context = {
        'brands': brands,
    }
    
    return render(request, 'admin_panel/brand_list.html', context)


@login_required
@user_passes_test(is_admin)
def brand_add(request):
    """Thêm thương hiệu mới."""
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        
        Brand.objects.create(
            name=name,
            slug=slug
        )
        
        messages.success(request, f'Đã thêm thương hiệu "{name}" thành công')
        return redirect('admin_brand_list')
    
    return render(request, 'admin_panel/brand_add.html')


@login_required
@user_passes_test(is_admin)
def brand_edit(request, brand_id):
    """Chỉnh sửa thương hiệu."""
    brand = get_object_or_404(Brand, id=brand_id)
    
    if request.method == 'POST':
        brand.name = request.POST.get('name')
        brand.slug = request.POST.get('slug')
        brand.save()
        
        messages.success(request, f'Đã cập nhật thương hiệu "{brand.name}" thành công')
        return redirect('admin_brand_list')
    
    context = {
        'brand': brand,
    }
    
    return render(request, 'admin_panel/brand_edit.html', context)


@login_required
@user_passes_test(is_admin)
def brand_delete(request, brand_id):
    """Xóa thương hiệu."""
    brand = get_object_or_404(Brand, id=brand_id)
    
    if request.method == 'POST':
        brand_name = brand.name
        brand.delete()
        
        messages.success(request, f'Đã xóa thương hiệu "{brand_name}" thành công')
        return redirect('admin_brand_list')
    
    context = {
        'brand': brand,
        'products_count': Product.objects.filter(brand=brand).count(),
    }
    
    return render(request, 'admin_panel/brand_delete.html', context)


# ORDER MANAGEMENT
@login_required
@user_passes_test(is_admin)
def order_list(request):
    """Danh sách đơn hàng."""
    orders = Order.objects.all().order_by('-created_at')
    
    # Lọc theo trạng thái
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) | 
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'admin_panel/order_list.html', context)


@login_required
@user_passes_test(is_admin)
def order_detail(request, order_id):
    """Chi tiết đơn hàng."""
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'admin_panel/order_detail.html', context)


@login_required
@user_passes_test(is_admin)
def order_update_status(request, order_id):
    """Cập nhật trạng thái đơn hàng."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        
        # Cập nhật các trường thời gian tương ứng
        if new_status == 'processing':
            order.confirmed_at = timezone.now()
        elif new_status == 'shipped':
            order.shipped_at = timezone.now()
        elif new_status == 'delivered':
            order.delivered_at = timezone.now()
        
        order.save()
        
        messages.success(request, f'Đã cập nhật trạng thái đơn hàng #{order.id} thành công')
        return redirect('admin_order_detail', order_id=order.id)
    
    return redirect('admin_order_detail', order_id=order.id)


# CUSTOMER MANAGEMENT
@login_required
@user_passes_test(is_admin)
def customer_list(request):
    """Danh sách khách hàng."""
    customers = Customer.objects.all().order_by('-created_at')
    
    # Tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(user__username__icontains=search_query) | 
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    context = {
        'customers': customers,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/customer_list.html', context)


@login_required
@user_passes_test(is_admin)
def customer_detail(request, customer_id):
    """Chi tiết khách hàng."""
    customer = get_object_or_404(Customer, id=customer_id)
    orders = Order.objects.filter(user=customer.user).order_by('-created_at')
    
    context = {
        'customer': customer,
        'orders': orders,
    }
    
    return render(request, 'admin_panel/customer_detail.html', context)


@login_required
@user_passes_test(is_admin)
def customer_toggle_status(request, customer_id):
    """Kích hoạt/Vô hiệu hóa tài khoản khách hàng."""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status == 'activate':
            customer.user.is_active = True
            messages.success(request, f'Đã kích hoạt tài khoản của khách hàng {customer.fullname}')
        else:
            customer.user.is_active = False
            messages.success(request, f'Đã vô hiệu hóa tài khoản của khách hàng {customer.fullname}')
        
        customer.user.save()
    
    return redirect('admin_customer_detail', customer_id=customer.id)


# REPORTS & STATISTICS
@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    """Báo cáo và thống kê."""
    context = {}
    return render(request, 'admin_panel/reports.html', context)


# SETTINGS
@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    """Cài đặt hệ thống."""
    context = {}
    return render(request, 'admin_panel/settings.html', context)


@login_required
@user_passes_test(is_admin)
def employee_list(request):
    """Danh sách nhân viên."""
    employees = Employee.objects.all()
    
    # Tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        employees = employees.filter(
            Q(user__username__icontains=search_query) | 
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    context = {
        'employees': employees,
        'search_query': search_query,
        'roles': Role.objects.all(),
    }
    
    return render(request, 'admin_panel/employee_list.html', context)


@login_required
@user_passes_test(is_admin)
def employee_add(request):
    """Thêm nhân viên mới."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role_id = request.POST.get('role')
        phone = request.POST.get('phone')
        
        # Tạo user mới
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Tạo nhân viên mới
        Employee.objects.create(
            user=user,
            role_id=role_id,
            phone=phone
        )
        
        messages.success(request, f'Đã thêm nhân viên "{username}" thành công')
        return redirect('admin_employee_list')
    
    context = {
        'roles': Role.objects.all(),
    }
    
    return render(request, 'admin_panel/employee_add.html', context)


@login_required
@user_passes_test(is_admin)
def employee_edit(request, employee_id):
    """Chỉnh sửa thông tin nhân viên."""
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        employee.user.first_name = request.POST.get('first_name')
        employee.user.last_name = request.POST.get('last_name')
        employee.user.email = request.POST.get('email')
        employee.role_id = request.POST.get('role')
        employee.phone = request.POST.get('phone')
        
        # Cập nhật mật khẩu nếu có
        password = request.POST.get('password')
        if password:
            employee.user.set_password(password)
        
        employee.user.save()
        employee.save()
        
        messages.success(request, f'Đã cập nhật thông tin nhân viên "{employee.user.username}" thành công')
        return redirect('admin_employee_list')
    
    context = {
        'employee': employee,
        'roles': Role.objects.all(),
    }
    
    return render(request, 'admin_panel/employee_edit.html', context)


@login_required
@user_passes_test(is_admin)
def employee_delete(request, employee_id):
    """Xóa nhân viên."""
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        username = employee.user.username
        # Xóa tài khoản người dùng liên kết (sẽ tự động xóa nhân viên)
        employee.user.delete()
        
        messages.success(request, f'Đã xóa nhân viên "{username}" thành công')
        return redirect('admin_employee_list')
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'admin_panel/employee_delete.html', context)


@login_required
@user_passes_test(is_admin)
def role_list(request):
    """Danh sách vai trò."""
    roles = Role.objects.all()
    
    context = {
        'roles': roles,
    }
    
    return render(request, 'admin_panel/role_list.html', context)


@login_required
@user_passes_test(is_admin)
def role_add(request):
    """Thêm vai trò mới."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        # Tạo vai trò mới
        role = Role.objects.create(
            name=name,
            description=description
        )
        
        # Xử lý quyền
        permissions = request.POST.getlist('permissions')
        for perm_id in permissions:
            role.permissions.add(Permission.objects.get(id=perm_id))
        
        messages.success(request, f'Đã thêm vai trò "{name}" thành công')
        return redirect('admin_role_list')
    
    context = {
        'permissions': Permission.objects.all(),
    }
    
    return render(request, 'admin_panel/role_add.html', context)


@login_required
@user_passes_test(is_admin)
def role_edit(request, role_id):
    """Chỉnh sửa vai trò."""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        role.name = request.POST.get('name')
        role.description = request.POST.get('description')
        role.save()
        
        # Cập nhật quyền
        role.permissions.clear()
        permissions = request.POST.getlist('permissions')
        for perm_id in permissions:
            role.permissions.add(Permission.objects.get(id=perm_id))
        
        messages.success(request, f'Đã cập nhật vai trò "{role.name}" thành công')
        return redirect('admin_role_list')
    
    context = {
        'role': role,
        'permissions': Permission.objects.all(),
        'role_permissions': [p.id for p in role.permissions.all()],
    }
    
    return render(request, 'admin_panel/role_edit.html', context)


@login_required
@user_passes_test(is_admin)
def role_delete(request, role_id):
    """Xóa vai trò."""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        role_name = role.name
        role.delete()
        
        messages.success(request, f'Đã xóa vai trò "{role_name}" thành công')
        return redirect('admin_role_list')
    
    context = {
        'role': role,
    }
    
    return render(request, 'admin_panel/role_delete.html', context)


@login_required
@user_passes_test(is_admin)
def supplier_list(request):
    """Danh sách nhà cung cấp."""
    suppliers = Supplier.objects.all()
    
    # Tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) | 
            Q(contact_info__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    context = {
        'suppliers': suppliers,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/supplier_list.html', context)


@login_required
@user_passes_test(is_admin)
def supplier_add(request):
    """Thêm nhà cung cấp mới."""
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_info = request.POST.get('contact_info')
        address = request.POST.get('address')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        # Tạo nhà cung cấp mới
        supplier = Supplier.objects.create(
            name=name,
            contact_info=contact_info,
            address=address,
            email=email,
            phone=phone
        )
        
        messages.success(request, f'Đã thêm nhà cung cấp "{name}" thành công')
        return redirect('admin_supplier_list')
    
    return render(request, 'admin_panel/supplier_add.html')


@login_required
@user_passes_test(is_admin)
def supplier_edit(request, supplier_id):
    """Chỉnh sửa nhà cung cấp."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        supplier.name = request.POST.get('name')
        supplier.contact_info = request.POST.get('contact_info')
        supplier.address = request.POST.get('address')
        supplier.email = request.POST.get('email')
        supplier.phone = request.POST.get('phone')
        supplier.is_active = 'is_active' in request.POST
        supplier.save()
        
        messages.success(request, f'Đã cập nhật nhà cung cấp "{supplier.name}" thành công')
        return redirect('admin_supplier_list')
    
    context = {
        'supplier': supplier,
    }
    
    return render(request, 'admin_panel/supplier_edit.html', context)


@login_required
@user_passes_test(is_admin)
def supplier_delete(request, supplier_id):
    """Xóa nhà cung cấp."""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        supplier_name = supplier.name
        supplier.delete()
        
        messages.success(request, f'Đã xóa nhà cung cấp "{supplier_name}" thành công')
        return redirect('admin_supplier_list')
    
    context = {
        'supplier': supplier,
    }
    
    return render(request, 'admin_panel/supplier_delete.html', context)


@login_required
@user_passes_test(is_admin)
def import_list(request):
    """Danh sách phiếu nhập."""
    imports = Import.objects.all()
    
    # Tìm kiếm
    search_query = request.GET.get('search', '')
    if search_query:
        imports = imports.filter(
            Q(supplier__name__icontains=search_query) | 
            Q(employee__user__username__icontains=search_query) |
            Q(note__icontains=search_query)
        )
    
    context = {
        'imports': imports,
        'search_query': search_query,
    }
    
    return render(request, 'admin_panel/import_list.html', context)


@login_required
@user_passes_test(is_admin)
def import_add(request):
    """Thêm phiếu nhập mới."""
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        employee_id = request.employee.id  # Nhân viên đang đăng nhập
        note = request.POST.get('note')
        
        # Tạo phiếu nhập mới
        import_obj = Import.objects.create(
            supplier_id=supplier_id,
            employee_id=employee_id,
            total=0,  # Sẽ cập nhật sau
            note=note
        )
        
        # Xử lý chi tiết phiếu nhập
        products = request.POST.getlist('products[]')
        quantities = request.POST.getlist('quantities[]')
        unit_prices = request.POST.getlist('unit_prices[]')
        
        total = 0
        for i in range(len(products)):
            product_id = products[i]
            quantity = int(quantities[i])
            unit_price = int(unit_prices[i])
            subtotal = quantity * unit_price
            
            # Tạo chi tiết phiếu nhập
            ImportDetail.objects.create(
                import_obj=import_obj,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price
            )
            
            # Cập nhật số lượng tồn kho
            product = Product.objects.get(id=product_id)
            product.stock += quantity
            product.save()
            
            total += subtotal
        
        # Cập nhật tổng tiền
        import_obj.total = total
        import_obj.save()
        
        messages.success(request, f'Đã tạo phiếu nhập #{import_obj.id} thành công')
        return redirect('admin_import_list')
    
    context = {
        'suppliers': Supplier.objects.filter(is_active=True),
        'products': Product.objects.filter(is_deleted=False),
    }
    
    return render(request, 'admin_panel/import_add.html', context)


@login_required
@user_passes_test(is_admin)
def import_detail(request, import_id):
    """Chi tiết phiếu nhập."""
    import_obj = get_object_or_404(Import, id=import_id)
    import_details = ImportDetail.objects.filter(import_obj=import_obj)
    
    context = {
        'import': import_obj,
        'import_details': import_details,
    }
    
    return render(request, 'admin_panel/import_detail.html', context)


@login_required
@user_passes_test(is_admin)
def statistics(request):
    """Trang thống kê tổng quan."""
    # Tính thống kê chung
    total_revenue = Order.objects.filter(status__in=['completed', 'delivered']).aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders = Order.objects.count()
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    
    # Thống kê theo thời gian (7 ngày, 30 ngày, 1 năm)
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    one_year_ago = now - timedelta(days=365)
    
    revenue_7_days = Order.objects.filter(created_at__gte=seven_days_ago, status__in=['completed', 'delivered']).aggregate(Sum('total_price'))['total_price__sum'] or 0
    revenue_30_days = Order.objects.filter(created_at__gte=thirty_days_ago, status__in=['completed', 'delivered']).aggregate(Sum('total_price'))['total_price__sum'] or 0
    revenue_1_year = Order.objects.filter(created_at__gte=one_year_ago, status__in=['completed', 'delivered']).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    orders_7_days = Order.objects.filter(created_at__gte=seven_days_ago).count()
    orders_30_days = Order.objects.filter(created_at__gte=thirty_days_ago).count()
    orders_1_year = Order.objects.filter(created_at__gte=one_year_ago).count()
    
    # Thống kê doanh thu theo tháng trong năm hiện tại
    current_year = now.year
    monthly_revenue = []
    for month in range(1, 13):
        month_revenue = Order.objects.filter(
            created_at__year=current_year,
            created_at__month=month,
            status__in=['completed', 'delivered']
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        monthly_revenue.append(month_revenue)
    
    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'revenue_7_days': revenue_7_days,
        'revenue_30_days': revenue_30_days,
        'revenue_1_year': revenue_1_year,
        'orders_7_days': orders_7_days,
        'orders_30_days': orders_30_days,
        'orders_1_year': orders_1_year,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'admin_panel/statistics.html', context)


@login_required
@user_passes_test(is_admin)
def product_statistics(request):
    """Thống kê sản phẩm."""
    # Sản phẩm bán chạy nhất
    best_selling_products = Product.objects.annotate(
        sold_quantity=Sum('order_items__quantity')
    ).order_by('-sold_quantity')[:10]
    
    # Danh mục bán chạy nhất
    best_selling_categories = Category.objects.annotate(
        sold_quantity=Sum('products__order_items__quantity')
    ).order_by('-sold_quantity')[:5]
    
    # Thương hiệu bán chạy nhất
    best_selling_brands = Brand.objects.annotate(
        sold_quantity=Sum('products__order_items__quantity')
    ).order_by('-sold_quantity')[:5]
    
    context = {
        'best_selling_products': best_selling_products,
        'best_selling_categories': best_selling_categories,
        'best_selling_brands': best_selling_brands,
    }
    
    return render(request, 'admin_panel/product_statistics.html', context)


@login_required
@user_passes_test(is_admin)
def customer_statistics(request):
    """Thống kê khách hàng."""
    # Khách hàng mua nhiều nhất
    top_customers = Customer.objects.annotate(
        total_spent=Sum('user__orders__total_price'),
        order_count=Count('user__orders')
    ).order_by('-total_spent')[:10]
    
    # Thông tin đăng ký khách hàng theo thời gian
    now = timezone.now()
    current_year = now.year
    customers_by_month = []
    for month in range(1, 13):
        count = Customer.objects.filter(
            created_at__year=current_year,
            created_at__month=month
        ).count()
        customers_by_month.append(count)
    
    context = {
        'top_customers': top_customers,
        'customers_by_month': customers_by_month,
    }
    
    return render(request, 'admin_panel/customer_statistics.html', context)


@login_required
@user_passes_test(is_admin)
def sales_statistics(request):
    """Thống kê doanh số."""
    # Doanh thu theo tháng
    now = timezone.now()
    current_year = now.year
    monthly_revenue = []
    for month in range(1, 13):
        month_revenue = Order.objects.filter(
            created_at__year=current_year,
            created_at__month=month,
            status__in=['completed', 'delivered']
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        monthly_revenue.append(month_revenue)
    
    # Đơn hàng theo trạng thái
    order_status_counts = {}
    for status, _ in Order.STATUS_CHOICES:
        count = Order.objects.filter(status=status).count()
        order_status_counts[status] = count
    
    # Phương thức thanh toán phổ biến
    payment_method_counts = {}
    for method, _ in Order.PAYMENT_METHOD_CHOICES:
        count = Order.objects.filter(payment_method=method).count()
        payment_method_counts[method] = count
    
    context = {
        'monthly_revenue': monthly_revenue,
        'order_status_counts': order_status_counts,
        'payment_method_counts': payment_method_counts,
    }
    
    return render(request, 'admin_panel/sales_statistics.html', context) 