from .models import Cart


def cart_processor(request):
    """
    Context processor để hiển thị thông tin giỏ hàng ở mọi trang.
    """
    cart_count = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_count = cart_items.count()
        cart_total = sum(item.subtotal for item in cart_items)
    
    return {
        'cart_count': cart_count,
        'cart_total': cart_total
    } 