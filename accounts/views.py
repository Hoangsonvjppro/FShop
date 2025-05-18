from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Customer, Address


def login_view(request):
    """Đăng nhập người dùng."""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """Đăng xuất người dùng."""
    logout(request)
    return redirect('home')


def register(request):
    """Đăng ký tài khoản mới."""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Kiểm tra mật khẩu nhập lại
        if password != password_confirm:
            messages.error(request, 'Mật khẩu nhập lại không khớp')
            return render(request, 'accounts/register.html')
        
        # Kiểm tra username đã tồn tại chưa
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại')
            return render(request, 'accounts/register.html')
        
        # Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng')
            return render(request, 'accounts/register.html')
        
        # Tạo tài khoản mới
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Tạo hồ sơ khách hàng
        Customer.objects.create(user=user)
        
        # Đăng nhập người dùng
        login(request, user)
        messages.success(request, 'Đăng ký tài khoản thành công')
        return redirect('home')
    
    return render(request, 'accounts/register.html')


@login_required
def profile(request):
    """Hiển thị trang thông tin cá nhân."""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        customer = Customer.objects.create(user=request.user)
    
    context = {
        'customer': customer
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit(request):
    """Chỉnh sửa thông tin cá nhân."""
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        customer = Customer.objects.create(user=request.user)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        # Kiểm tra email đã tồn tại chưa
        if User.objects.exclude(id=request.user.id).filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng')
            return redirect('profile_edit')
        
        # Cập nhật thông tin người dùng
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        # Cập nhật thông tin khách hàng
        customer.phone = phone
        
        # Xử lý ảnh đại diện
        if 'avatar' in request.FILES:
            customer.avatar = request.FILES['avatar']
        
        customer.save()
        
        messages.success(request, 'Cập nhật thông tin cá nhân thành công')
        return redirect('profile')
    
    context = {
        'customer': customer
    }
    
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def change_password(request):
    """Thay đổi mật khẩu."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Thay đổi mật khẩu thành công')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form
    }
    
    return render(request, 'accounts/change_password.html', context)


@login_required
def address_list(request):
    """Hiển thị danh sách địa chỉ."""
    try:
        customer = request.user.customer
        addresses = Address.objects.filter(customers=customer)
    except Customer.DoesNotExist:
        customer = Customer.objects.create(user=request.user)
        addresses = []
    
    context = {
        'addresses': addresses
    }
    
    return render(request, 'accounts/address_list.html', context)


@login_required
def address_add(request):
    """Thêm địa chỉ mới."""
    if request.method == 'POST':
        province = request.POST.get('province')
        district = request.POST.get('district')
        ward = request.POST.get('ward')
        detail = request.POST.get('detail')
        
        if not all([province, district, ward, detail]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin địa chỉ')
            return redirect('address_add')
        
        # Tạo địa chỉ mới
        address = Address.objects.create(
            province=province,
            district=district,
            ward=ward,
            detail=detail
        )
        
        # Liên kết địa chỉ với khách hàng
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            customer = Customer.objects.create(user=request.user)
        
        # Nếu chưa có địa chỉ nào, đặt địa chỉ này làm địa chỉ mặc định
        if not Address.objects.filter(customers=customer).exists():
            customer.address = address
            customer.save()
        
        messages.success(request, 'Thêm địa chỉ mới thành công')
        return redirect('address_list')
    
    return render(request, 'accounts/address_add.html')


@login_required
def address_edit(request, address_id):
    """Chỉnh sửa địa chỉ."""
    address = get_object_or_404(Address, id=address_id)
    
    if request.method == 'POST':
        province = request.POST.get('province')
        district = request.POST.get('district')
        ward = request.POST.get('ward')
        detail = request.POST.get('detail')
        
        if not all([province, district, ward, detail]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin địa chỉ')
            return redirect('address_edit', address_id=address.id)
        
        # Cập nhật địa chỉ
        address.province = province
        address.district = district
        address.ward = ward
        address.detail = detail
        address.save()
        
        messages.success(request, 'Cập nhật địa chỉ thành công')
        return redirect('address_list')
    
    context = {
        'address': address
    }
    
    return render(request, 'accounts/address_edit.html', context)


@login_required
def address_delete(request, address_id):
    """Xóa địa chỉ."""
    address = get_object_or_404(Address, id=address_id)
    
    # Kiểm tra nếu địa chỉ này là địa chỉ mặc định của khách hàng
    try:
        customer = request.user.customer
        if customer.address == address:
            # Nếu còn địa chỉ khác, đặt địa chỉ đầu tiên làm mặc định
            other_addresses = Address.objects.filter(customers=customer).exclude(id=address.id)
            if other_addresses.exists():
                customer.address = other_addresses.first()
            else:
                customer.address = None
            customer.save()
    except Customer.DoesNotExist:
        pass
    
    address.delete()
    messages.success(request, 'Xóa địa chỉ thành công')
    
    return redirect('address_list') 