from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from products.models import Product
from cart.models import Cart
from accounts.models import Address, Customer
from .models import Order, OrderItem


@login_required
def checkout(request):
    """Hiển thị trang thanh toán."""
    cart_items = Cart.objects.filter(user=request.user)
    
    # Kiểm tra giỏ hàng có sản phẩm không
    if not cart_items.exists():
        messages.warning(request, 'Giỏ hàng của bạn đang trống')
        return redirect('cart_detail')
        
    # Kiểm tra số lượng tồn kho
    invalid_items = []
    for item in cart_items:
        if item.quantity > item.product.stock:
            if item.product.stock == 0:
                invalid_items.append({
                    'product': item.product,
                    'message': f'Sản phẩm "{item.product.name}" đã hết hàng'
                })
            else:
                invalid_items.append({
                    'product': item.product,
                    'message': f'Sản phẩm "{item.product.name}" chỉ còn {item.product.stock} trong kho'
                })
    
    if invalid_items:
        context = {
            'invalid_items': invalid_items,
            'cart_items': cart_items
        }
        return render(request, 'orders/invalid_cart.html', context)
    
    # Tính tổng tiền
    subtotal = sum(item.subtotal for item in cart_items)
    shipping_fee = 30000  # Phí vận chuyển cố định, có thể thay đổi tùy theo địa chỉ
    total = subtotal + shipping_fee
    
    # Lấy địa chỉ của người dùng
    try:
        customer = request.user.customer
        addresses = Address.objects.filter(customers=customer)
    except Customer.DoesNotExist:
        addresses = []
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total': total,
        'addresses': addresses
    }
    
    return render(request, 'orders/checkout.html', context)


@login_required
def order_create(request):
    """Tạo đơn hàng mới."""
    if request.method != 'POST':
        return redirect('checkout')
    
    cart_items = Cart.objects.filter(user=request.user)
    
    # Kiểm tra giỏ hàng có sản phẩm không
    if not cart_items.exists():
        messages.warning(request, 'Giỏ hàng của bạn đang trống')
        return redirect('cart_detail')
    
    # Lấy thông tin từ form
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    note = request.POST.get('note', '')
    payment_method = request.POST.get('payment_method')
    shipping_method = request.POST.get('shipping_method', 'standard')
    
    # Tính phí giao hàng dựa trên phương thức
    shipping_fee = 50000 if shipping_method == 'express' else 30000
    
    # Xử lý địa chỉ
    address_id = request.POST.get('address_id')
    shipping_address = ""
    
    if address_id:
        try:
            # Sử dụng địa chỉ có sẵn
            address = Address.objects.get(id=address_id)
            shipping_address = address.get_full_address()
        except Address.DoesNotExist:
            # Nếu không tìm thấy địa chỉ, chuyển hướng về checkout
            messages.error(request, 'Vui lòng chọn hoặc nhập địa chỉ giao hàng')
            return redirect('checkout')
    else:
        # Tạo địa chỉ từ form
        province = request.POST.get('province')
        district = request.POST.get('district')
        ward = request.POST.get('ward')
        street = request.POST.get('street')
        
        # Lấy text của các select option
        province_text = dict(zip(
            [option.split('"')[1] for option in str(request.POST).split('value="')[1:] if 'province' in str(option)],
            [option.split('>')[1].split('<')[0] for option in str(request.POST).split('<option')[1:] if 'province' in str(option)]
        )).get(province, '')
        
        district_text = "Quận/Huyện"  # Fallback
        ward_text = "Phường/Xã"       # Fallback
        
        if province and district and ward and street:
            shipping_address = f"{street}, {ward_text}, {district_text}, {province_text}"
        else:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin địa chỉ')
            return redirect('checkout')
    
    # Kiểm tra dữ liệu cần thiết
    if not all([full_name, email, phone, shipping_address, payment_method]):
        messages.error(request, 'Vui lòng điền đầy đủ thông tin')
        return redirect('checkout')
    
    # Tính tổng tiền
    subtotal = sum(item.subtotal for item in cart_items)
    total = subtotal + shipping_fee
    
    # Tạo đơn hàng
    order = Order.objects.create(
        user=request.user,
        full_name=full_name,
        email=email,
        phone=phone,
        shipping_address=shipping_address,
        note=note,
        total_price=subtotal,
        shipping_fee=shipping_fee,
        payment_method=payment_method,
        status='pending'
    )
    
    # Tạo chi tiết đơn hàng
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.product.price,
            quantity=item.quantity
        )
    
    # Xóa giỏ hàng sau khi đặt hàng
    cart_items.delete()
    
    messages.success(request, 'Đặt hàng thành công! Cảm ơn bạn đã mua hàng.')
    return redirect('order_complete', order_id=order.id)


@login_required
def order_complete(request, order_id):
    """Trang cảm ơn sau khi đặt hàng thành công."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order
    }
    
    return render(request, 'orders/order_complete.html', context)


@login_required
def order_history(request):
    """Hiển thị danh sách đơn hàng của người dùng."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders
    }
    
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail(request, order_id):
    """Hiển thị chi tiết đơn hàng."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_cancel(request, order_id):
    """Hủy đơn hàng."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Chỉ cho phép hủy đơn hàng ở trạng thái "chờ xác nhận"
    if order.status != 'pending':
        messages.error(request, 'Không thể hủy đơn hàng này')
        return redirect('order_detail', order_id=order.id)
    
    # Cập nhật trạng thái đơn hàng
    order.status = 'cancelled'
    order.save()
    
    messages.success(request, 'Đơn hàng đã được hủy thành công')
    
    return redirect('order_detail', order_id=order.id) 