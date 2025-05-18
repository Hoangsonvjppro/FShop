from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', verbose_name="Người dùng")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='carts', verbose_name="Sản phẩm")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"
        unique_together = ['user', 'product']
        
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"
        
    @property
    def subtotal(self):
        return self.quantity * self.product.price


class SavedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items', verbose_name="Người dùng")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='saved_by', verbose_name="Sản phẩm")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày lưu")
    
    class Meta:
        verbose_name = "Sản phẩm đã lưu"
        verbose_name_plural = "Sản phẩm đã lưu"
        unique_together = ['user', 'product']
        
    def __str__(self):
        return f"{self.user.username} - {self.product.name}" 