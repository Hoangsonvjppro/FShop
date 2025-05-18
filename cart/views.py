from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Cart, SavedItem


@login_required
def cart_detail(request):
    """Hiển thị chi tiết giỏ hàng."""
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.subtotal for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'cart/cart_detail.html', context)


@login_required
def cart_add(request, product_id):
    """Thêm sản phẩm vào giỏ hàng."""
    product = get_object_or_404(Product, id=product_id, available=True, is_deleted=False)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        messages.error(request, 'Số lượng phải lớn hơn 0')
        return redirect('product_detail', id=product.id, slug=product.slug)
    
    # Kiểm tra số lượng tồn kho
    if quantity > product.stock:
        messages.error(request, f'Chỉ còn {product.stock} sản phẩm trong kho')
        
        # Xử lý yêu cầu Ajax
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': f'Chỉ còn {product.stock} sản phẩm trong kho'
            })
            
        return redirect('product_detail', id=product.id, slug=product.slug)
    
    # Kiểm tra sản phẩm đã có trong giỏ hàng chưa
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    # Nếu sản phẩm đã có trong giỏ hàng, cập nhật số lượng
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            msg = f'Giỏ hàng đã có {cart_item.quantity} sản phẩm. Chỉ còn {product.stock} sản phẩm trong kho'
            messages.error(request, msg)
            
            # Xử lý yêu cầu Ajax
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': msg
                })
                
            return redirect('product_detail', id=product.id, slug=product.slug)
            
        cart_item.quantity = new_quantity
        cart_item.save()
    
    messages.success(request, f'Đã thêm "{product.name}" vào giỏ hàng')
    
    # Xử lý yêu cầu Ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_count = Cart.objects.filter(user=request.user).count()
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.subtotal for item in cart_items)
        return JsonResponse({
            'success': True,
            'message': f'Đã thêm "{product.name}" vào giỏ hàng',
            'cart_count': cart_count,
            'total': total
        })
        
    return redirect('cart_detail')


@login_required
def cart_remove(request, product_id):
    """Xóa sản phẩm khỏi giỏ hàng."""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = Cart.objects.get(user=request.user, product=product)
        cart_item.delete()
        messages.success(request, f'Đã xóa "{product.name}" khỏi giỏ hàng')
    except Cart.DoesNotExist:
        pass
    
    # Xử lý yêu cầu Ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_count = Cart.objects.filter(user=request.user).count()
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.subtotal for item in cart_items)
        return JsonResponse({
            'success': True,
            'message': f'Đã xóa "{product.name}" khỏi giỏ hàng',
            'cart_count': cart_count,
            'total': total
        })
        
    return redirect('cart_detail')


@login_required
def cart_update(request, product_id):
    """Cập nhật số lượng sản phẩm trong giỏ hàng."""
    product = get_object_or_404(Product, id=product_id, available=True, is_deleted=False)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        return cart_remove(request, product_id)
    
    # Kiểm tra số lượng tồn kho
    if quantity > product.stock:
        messages.error(request, f'Chỉ còn {product.stock} sản phẩm trong kho')
        
        # Xử lý yêu cầu Ajax
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Chỉ còn {product.stock} sản phẩm trong kho'
            })
            
        return redirect('cart_detail')
    
    # Cập nhật số lượng sản phẩm trong giỏ hàng
    try:
        cart_item = Cart.objects.get(user=request.user, product=product)
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f'Đã cập nhật số lượng "{product.name}" trong giỏ hàng')
    except Cart.DoesNotExist:
        cart_item = Cart.objects.create(user=request.user, product=product, quantity=quantity)
        messages.success(request, f'Đã thêm "{product.name}" vào giỏ hàng')
    
    # Xử lý yêu cầu Ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.subtotal for item in cart_items)
        return JsonResponse({
            'success': True,
            'message': f'Đã cập nhật số lượng "{product.name}" trong giỏ hàng',
            'quantity': cart_item.quantity,
            'subtotal': cart_item.subtotal,
            'total': total
        })
        
    return redirect('cart_detail')


@login_required
def cart_clear(request):
    """Xóa tất cả sản phẩm trong giỏ hàng."""
    Cart.objects.filter(user=request.user).delete()
    messages.success(request, 'Đã xóa tất cả sản phẩm trong giỏ hàng')
    return redirect('cart_detail')


@login_required
def saved_items(request):
    """Hiển thị danh sách sản phẩm đã lưu."""
    saved_items = SavedItem.objects.filter(user=request.user)
    
    context = {
        'saved_items': saved_items,
    }
    return render(request, 'cart/saved_items.html', context)


@login_required
def save_item(request, product_id):
    """Lưu sản phẩm vào danh sách yêu thích."""
    product = get_object_or_404(Product, id=product_id)
    
    # Kiểm tra sản phẩm đã có trong danh sách yêu thích chưa
    saved_item, created = SavedItem.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'Đã lưu "{product.name}" vào danh sách yêu thích')
    else:
        messages.info(request, f'"{product.name}" đã có trong danh sách yêu thích')
    
    # Xử lý yêu cầu Ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'created': created,
            'message': f'Đã lưu "{product.name}" vào danh sách yêu thích' if created else f'"{product.name}" đã có trong danh sách yêu thích'
        })
        
    return redirect('product_detail', id=product.id, slug=product.slug)


@login_required
def unsave_item(request, product_id):
    """Xóa sản phẩm khỏi danh sách yêu thích."""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        saved_item = SavedItem.objects.get(user=request.user, product=product)
        saved_item.delete()
        messages.success(request, f'Đã xóa "{product.name}" khỏi danh sách yêu thích')
    except SavedItem.DoesNotExist:
        messages.info(request, f'"{product.name}" không có trong danh sách yêu thích')
    
    # Xử lý yêu cầu Ajax
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Đã xóa "{product.name}" khỏi danh sách yêu thích'
        })
        
    # Xác định trang referer để chuyển hướng người dùng về trang trước đó
    referer = request.META.get('HTTP_REFERER')
    if referer and 'saved-items' in referer:
        return redirect('saved_items')
    
    return redirect('product_detail', id=product.id, slug=product.slug) 