from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Statistic(models.Model):
    date = models.DateField(verbose_name="Ngày")
    total_sales = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Tổng doanh thu")
    total_orders = models.PositiveIntegerField(default=0, verbose_name="Tổng đơn hàng")
    total_users = models.PositiveIntegerField(default=0, verbose_name="Tổng người dùng")
    
    class Meta:
        verbose_name = "Thống kê"
        verbose_name_plural = "Thống kê"
        ordering = ['-date']
        
    def __str__(self):
        return f"Thống kê ngày {self.date.strftime('%d/%m/%Y')}"


class ProductStatistic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='statistics', verbose_name="Sản phẩm")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Lượt xem")
    order_count = models.PositiveIntegerField(default=0, verbose_name="Lượt mua")
    date = models.DateField(verbose_name="Ngày")
    
    class Meta:
        verbose_name = "Thống kê sản phẩm"
        verbose_name_plural = "Thống kê sản phẩm"
        unique_together = ['product', 'date']
        ordering = ['-date']
        
    def __str__(self):
        return f"Thống kê sản phẩm {self.product.name} - {self.date.strftime('%d/%m/%Y')}"


class UserStatistic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statistics', verbose_name="Người dùng")
    order_count = models.PositiveIntegerField(default=0, verbose_name="Số đơn hàng")
    total_spent = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="Tổng chi tiêu")
    date = models.DateField(verbose_name="Ngày")
    
    class Meta:
        verbose_name = "Thống kê người dùng"
        verbose_name_plural = "Thống kê người dùng"
        unique_together = ['user', 'date']
        ordering = ['-date']
        
    def __str__(self):
        return f"Thống kê người dùng {self.user.username} - {self.date.strftime('%d/%m/%Y')}" 