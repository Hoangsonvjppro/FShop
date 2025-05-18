from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from accounts.models import Address


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('credit_card', 'Thẻ tín dụng/ghi nợ'),
        ('e_wallet', 'Ví điện tử'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Khách hàng")
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='orders', verbose_name="Địa chỉ giao hàng")
    shipping_address = models.TextField(blank=True, verbose_name="Địa chỉ giao hàng")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    total_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Tổng tiền")
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Phí vận chuyển")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod', verbose_name="Phương thức thanh toán")
    is_paid = models.BooleanField(default=False, verbose_name="Đã thanh toán")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.full_name}"
        
    @property
    def grand_total(self):
        return self.total_price + self.shipping_fee
        
    def get_status_display_class(self):
        status_classes = {
            'pending': 'bg-gray-200',
            'processing': 'bg-blue-200 text-blue-800',
            'shipped': 'bg-indigo-200 text-indigo-800',
            'delivered': 'bg-teal-200 text-teal-800',
            'completed': 'bg-green-200 text-green-800',
            'cancelled': 'bg-red-200 text-red-800',
        }
        return status_classes.get(self.status, 'bg-gray-200')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Đơn hàng")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name="Sản phẩm")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    
    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
        
    @property
    def subtotal(self):
        return self.price * self.quantity 