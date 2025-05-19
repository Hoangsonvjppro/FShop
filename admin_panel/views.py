from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from accounts.models import Customer, Employee, Role, Permission, RolePermission
from products.models import Product, Category, Brand, ProductImage, Supplier, Import, ImportDetail
from orders.models import Order, OrderItem
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from functools import wraps


def create_default_permissions():
    """
    Tạo các quyền mặc định trong hệ thống.
    Hàm này nên được gọi khi khởi tạo database
    """
    default_permissions = [
        # Quyền quản lý sản phẩm
        {"code": "product_view", "name": "Xem danh sách sản phẩm"},
        {"code": "product_add", "name": "Thêm sản phẩm mới"},
        {"code": "product_edit", "name": "Chỉnh sửa sản phẩm"},
        {"code": "product_delete", "name": "Xóa sản phẩm"},
        
        # Quyền quản lý danh mục
        {"code": "category_view", "name": "Xem danh sách danh mục"},
        {"code": "category_add", "name": "Thêm danh mục mới"},
        {"code": "category_edit", "name": "Chỉnh sửa danh mục"},
        {"code": "category_delete", "name": "Xóa danh mục"},
        
        # Quyền quản lý thương hiệu
        {"code": "brand_view", "name": "Xem danh sách thương hiệu"},
        {"code": "brand_add", "name": "Thêm thương hiệu mới"},
        {"code": "brand_edit", "name": "Chỉnh sửa thương hiệu"},
        {"code": "brand_delete", "name": "Xóa thương hiệu"},
        
        # Quyền quản lý đơn hàng
        {"code": "order_view", "name": "Xem danh sách đơn hàng"},
        {"code": "order_detail", "name": "Xem chi tiết đơn hàng"},
        {"code": "order_update", "name": "Cập nhật trạng thái đơn hàng"},
        {"code": "order_cancel", "name": "Hủy đơn hàng"},
        
        # Quyền quản lý khách hàng
        {"code": "customer_view", "name": "Xem danh sách khách hàng"},
        {"code": "customer_detail", "name": "Xem chi tiết khách hàng"},
        {"code": "customer_update", "name": "Cập nhật thông tin khách hàng"},
        
        # Quyền quản lý nhân viên
        {"code": "employee_view", "name": "Xem danh sách nhân viên"},
        {"code": "employee_add", "name": "Thêm nhân viên mới"},
        {"code": "employee_edit", "name": "Chỉnh sửa thông tin nhân viên"},
        {"code": "employee_delete", "name": "Xóa nhân viên"},
        
        # Quyền quản lý vai trò
        {"code": "role_view", "name": "Xem danh sách vai trò"},
        {"code": "role_add", "name": "Thêm vai trò mới"},
        {"code": "role_edit", "name": "Chỉnh sửa vai trò"},
        {"code": "role_delete", "name": "Xóa vai trò"},
        
        # Quyền quản lý nhà cung cấp
        {"code": "supplier_view", "name": "Xem danh sách nhà cung cấp"},
        {"code": "supplier_add", "name": "Thêm nhà cung cấp mới"},
        {"code": "supplier_edit", "name": "Chỉnh sửa nhà cung cấp"},
        {"code": "supplier_delete", "name": "Xóa nhà cung cấp"},
        
        # Quyền quản lý nhập kho
        {"code": "import_view", "name": "Xem danh sách phiếu nhập kho"},
        {"code": "import_add", "name": "Tạo phiếu nhập kho mới"},
        {"code": "import_detail", "name": "Xem chi tiết phiếu nhập kho"},
        
        # Quyền xem báo cáo thống kê
        {"code": "report_view", "name": "Xem báo cáo thống kê"},
        {"code": "stat_product", "name": "Xem thống kê sản phẩm"},
        {"code": "stat_customer", "name": "Xem thống kê khách hàng"},
        {"code": "stat_sales", "name": "Xem thống kê doanh số"}
    ]
    
    # Tạo các quyền nếu chưa tồn tại
    for perm in default_permissions:
        Permission.objects.get_or_create(code=perm["code"], defaults={"name": perm["name"]})
    
    # Tạo vai trò mặc định cho Admin với tất cả quyền
    admin_role, created = Role.objects.get_or_create(
        name="Admin", 
        defaults={"slug": "admin"}
    )
    
    if created:
        # Gán tất cả quyền cho vai trò Admin
        for perm in Permission.objects.all():
            RolePermission.objects.get_or_create(role=admin_role, permission=perm)
    
    # Tạo vai trò cho Nhân viên bán hàng
    sales_role, created = Role.objects.get_or_create(
        name="Nhân viên bán hàng", 
        defaults={"slug": "sales-staff"}
    )
    
    if created:
        # Danh sách mã quyền cho nhân viên bán hàng
        sales_permissions = [
            "product_view", "category_view", "brand_view",
            "order_view", "order_detail", "order_update",
            "customer_view", "customer_detail"
        ]
        
        # Gán quyền cho vai trò nhân viên bán hàng
        for perm_code in sales_permissions:
            try:
                perm = Permission.objects.get(code=perm_code)
                RolePermission.objects.get_or_create(role=sales_role, permission=perm)
            except Permission.DoesNotExist:
                continue
    
    # Tạo vai trò cho Nhân viên kho
    inventory_role, created = Role.objects.get_or_create(
        name="Nhân viên kho", 
        defaults={"slug": "inventory-staff"}
    )
    
    if created:
        # Danh sách mã quyền cho nhân viên kho
        inventory_permissions = [
            "product_view", "product_edit", "category_view", "brand_view",
            "supplier_view", "import_view", "import_add", "import_detail"
        ]
        
        # Gán quyền cho vai trò nhân viên kho
        for perm_code in inventory_permissions:
            try:
                perm = Permission.objects.get(code=perm_code)
                RolePermission.objects.get_or_create(role=inventory_role, permission=perm)
            except Permission.DoesNotExist:
                continue


def is_admin(user):
    """Kiểm tra người dùng có quyền admin."""
    try:
        return user.is_authenticated and hasattr(user, 'employee') and user.employee.role is not None
    except:
        return False


def permission_required(permission_code):
    """
    Decorator kiểm tra quyền truy cập theo mã quyền.
    Sử dụng: @permission_required('product_view')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Kiểm tra người dùng có quyền không
            if not hasattr(request.user, 'employee'):
                return render(request, 'admin_panel/permission_denied.html', {
                    'missing_permissions': [permission_code]
                })
                
            if not request.user.employee.has_permission(permission_code):
                # Trả về trang lỗi không có quyền truy cập
                return render(request, 'admin_panel/permission_denied.html', {
                    'missing_permissions': [permission_code]
                })
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def permissions_required(permission_codes):
    """
    Decorator kiểm tra người dùng có nhiều quyền khác nhau.
    Sử dụng: @permissions_required(['product_view', 'product_edit'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Kiểm tra người dùng có quyền không
            if not hasattr(request.user, 'employee'):
                return render(request, 'admin_panel/permission_denied.html', {
                    'missing_permissions': permission_codes
                })
                
            if not request.user.employee.has_permissions(permission_codes):
                missing_permissions = []
                for code in permission_codes:
                    if not request.user.employee.has_permission(code):
                        missing_permissions.append(code)
                
                # Trả về trang lỗi không có quyền truy cập
                return render(request, 'admin_panel/permission_denied.html', {
                    'missing_permissions': missing_permissions
                })
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def any_permission_required(permission_codes):
    """
    Decorator kiểm tra người dùng có ít nhất một quyền trong danh sách.
    Sử dụng: @any_permission_required(['product_edit', 'product_add'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Kiểm tra người dùng có quyền không
            if not hasattr(request.user, 'employee'):
                return render(request, 'admin_panel/permission_denied.html', {
                    'missing_permissions': permission_codes
                })
                
            if not request.user.employee.has_any_permission(permission_codes):
                # Trả về trang lỗi không có quyền truy cập
                return render(request, 'admin_panel/permission_denied.html', {
                    'missing_permissions': permission_codes
                })
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


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
@permission_required('product_view')
def product_list(request):
    """Danh sách sản phẩm."""
    try:
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
        
        # Chuyển đổi queryset thành list để xử lý các giá trị không hợp lệ
        product_list = []
        for product in products:
            try:
                # Kiểm tra giá trị price
                if not isinstance(product.price, (int, float, complex)) and product.price is not None:
                    # Nếu price không phải số và không phải None, thử chuyển đổi
                    try:
                        product.price = float(str(product.price).replace(',', ''))
                    except (ValueError, TypeError):
                        product.price = 0
                product_list.append(product)
            except Exception:
                # Bỏ qua sản phẩm có dữ liệu lỗi
                continue
        
        context = {
            'products': product_list,
            'filter': filter_option,
            'search_query': search_query,
            'categories': Category.objects.all(),
            'brands': Brand.objects.all(),
        }
        
        return render(request, 'admin_panel/product_list.html', context)
    except Exception as e:
        # Trong trường hợp có lỗi không xác định, hiển thị thông báo lỗi
        messages.error(request, f'Đã xảy ra lỗi khi tải danh sách sản phẩm: {str(e)}')
        return redirect('admin_dashboard')


@login_required
@permission_required('product_add')
def product_add(request):
    """Thêm sản phẩm mới."""
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        description = request.POST.get('description')
        
        # Xử lý giá tiền để đảm bảo là số hợp lệ
        try:
            price = request.POST.get('price', '0')
            # Xóa dấu phẩy hàng nghìn nếu có
            price = price.replace(',', '')
            price = float(price)
        except (ValueError, TypeError):
            price = 0
            
        # Xử lý số lượng tồn kho
        try:
            stock = int(request.POST.get('stock', '0'))
        except (ValueError, TypeError):
            stock = 0
            
        room_type = request.POST.get('room_type')
        material = request.POST.get('material')
        dimensions = request.POST.get('dimensions')
        
        # Xử lý trọng lượng
        try:
            weight = float(request.POST.get('weight', '0'))
        except (ValueError, TypeError):
            weight = 0
            
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
@permission_required('product_edit')
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
        
        # Xử lý giá tiền để đảm bảo là số hợp lệ
        try:
            price = request.POST.get('price', '0')
            # Xóa dấu phẩy hàng nghìn nếu có
            price = price.replace(',', '')
            product.price = float(price)
        except (ValueError, TypeError):
            product.price = 0
            
        # Xử lý số lượng tồn kho
        try:
            product.stock = int(request.POST.get('stock', '0'))
        except (ValueError, TypeError):
            product.stock = 0
            
        product.room_type = request.POST.get('room_type')
        product.material = request.POST.get('material')
        product.dimensions = request.POST.get('dimensions')
        
        # Xử lý trọng lượng
        try:
            weight = request.POST.get('weight', '0')
            product.weight = float(weight)
        except (ValueError, TypeError):
            product.weight = 0
            
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
@permission_required('product_delete')
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


@login_required
@user_passes_test(is_admin)
def order_cancel(request, order_id):
    """Hủy đơn hàng."""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Chỉ cho phép hủy đơn hàng ở trạng thái "chờ xác nhận"
        if order.status != 'pending' and order.status != 'confirmed':
            messages.error(request, f'Không thể hủy đơn hàng #{order.id} do đơn hàng không ở trạng thái cho phép hủy')
        else:
            order.status = 'cancelled'
            order.cancelled_at = timezone.now()
            order.save()
            
            messages.success(request, f'Đã hủy đơn hàng #{order.id} thành công')
    
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
@permission_required('role_view')
def role_list(request):
    """Danh sách vai trò."""
    roles = Role.objects.all()
    permissions = Permission.objects.all().order_by('code')
    
    context = {
        'roles': roles,
        'permissions': permissions,
    }
    
    return render(request, 'admin_panel/role_list.html', context)


@login_required
@permission_required('role_add')
def role_add(request):
    """Thêm vai trò mới."""
    if request.method == 'POST':
        name = request.POST.get('name')
        
        # Tạo vai trò mới
        role = Role.objects.create(
            name=name
        )
        
        # Xử lý quyền
        permissions = request.POST.getlist('permissions')
        for perm_id in permissions:
            permission = Permission.objects.get(id=perm_id)
            RolePermission.objects.create(role=role, permission=permission)
        
        messages.success(request, f'Đã thêm vai trò "{name}" thành công')
        return redirect('admin_role_list')
    
    context = {
        'permissions': Permission.objects.all(),
    }
    
    return render(request, 'admin_panel/role_add.html', context)


@login_required
@permission_required('role_edit')
def role_edit(request, role_id):
    """Chỉnh sửa vai trò."""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        role.name = request.POST.get('name')
        role.save()
        
        # Cập nhật quyền
        RolePermission.objects.filter(role=role).delete()
        permissions = request.POST.getlist('permissions')
        for perm_id in permissions:
            permission = Permission.objects.get(id=perm_id)
            RolePermission.objects.create(role=role, permission=permission)
        
        messages.success(request, f'Đã cập nhật vai trò "{role.name}" thành công')
        return redirect('admin_role_list')
    
    context = {
        'role': role,
        'permissions': Permission.objects.all(),
        'role_permissions': [p.permission.id for p in RolePermission.objects.filter(role=role)],
    }
    
    return render(request, 'admin_panel/role_edit.html', context)


@login_required
@permission_required('role_delete')
def role_delete(request, role_id):
    """Xóa vai trò."""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        # Kiểm tra xem vai trò đó có đang được sử dụng không
        if Employee.objects.filter(role=role).exists():
            messages.error(request, f'Không thể xóa vai trò "{role.name}" vì đang được gán cho nhân viên')
            return redirect('admin_role_list')
        
        role_name = role.name
        role.delete()
        
        messages.success(request, f'Đã xóa vai trò "{role_name}" thành công')
        return redirect('admin_role_list')
    
    context = {
        'role': role,
        'employee_count': Employee.objects.filter(role=role).count(),
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
        employee_id = request.user.employee.id  # Nhân viên đang đăng nhập
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
            if not products[i]:  # Bỏ qua dòng trống
                continue
                
            # Xử lý số lượng
            try:
                quantity = int(quantities[i]) if quantities[i] else 1
            except (ValueError, TypeError):
                quantity = 1
                
            # Xử lý đơn giá
            try:
                unit_price_str = unit_prices[i].strip() if unit_prices[i] else '0'
                unit_price_str = unit_price_str.replace(',', '')  # Xóa dấu phẩy nếu có
                unit_price = int(float(unit_price_str))
            except (ValueError, TypeError):
                unit_price = 0
                
            subtotal = quantity * unit_price
            
            # Tạo chi tiết phiếu nhập
            ImportDetail.objects.create(
                import_obj=import_obj,
                product_id=products[i],
                quantity=quantity,
                unit_price=unit_price
            )
            
            # Cập nhật số lượng tồn kho
            product = Product.objects.get(id=products[i])
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