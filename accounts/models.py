from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Address(models.Model):
    province = models.CharField(max_length=100, verbose_name="Tỉnh/Thành phố")
    district = models.CharField(max_length=100, verbose_name="Quận/Huyện")
    ward = models.CharField(max_length=100, verbose_name="Phường/Xã")
    detail = models.CharField(max_length=255, verbose_name="Địa chỉ chi tiết")
    
    class Meta:
        verbose_name = "Địa chỉ"
        verbose_name_plural = "Địa chỉ"
        
    def __str__(self):
        return f"{self.detail}, {self.ward}, {self.district}, {self.province}"
        
    def get_full_address(self):
        return f"{self.detail}, {self.ward}, {self.district}, {self.province}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', verbose_name="Tài khoản")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers', verbose_name="Địa chỉ")
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d', blank=True, verbose_name="Ảnh đại diện")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    
    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"
        
    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Role(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên vai trò")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    
    class Meta:
        verbose_name = "Vai trò"
        verbose_name_plural = "Vai trò"
        
    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def has_permission(self, permission_code):
        """Kiểm tra xem vai trò có quyền với mã code đã cho không"""
        return Permission.objects.filter(
            rolepermission__role=self,
            code=permission_code
        ).exists()


class Permission(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên quyền")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã quyền")
    
    class Meta:
        verbose_name = "Quyền"
        verbose_name_plural = "Quyền"
        
    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions', verbose_name="Vai trò")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions', verbose_name="Quyền")
    
    class Meta:
        verbose_name = "Quyền của vai trò"
        verbose_name_plural = "Quyền của vai trò"
        unique_together = ['role', 'permission']
        
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee', verbose_name="Tài khoản")
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='employees', verbose_name="Vai trò")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại")
    address = models.CharField(max_length=255, blank=True, verbose_name="Địa chỉ")
    avatar = models.ImageField(upload_to='employee_avatars/%Y/%m/%d', blank=True, verbose_name="Ảnh đại diện")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    
    class Meta:
        verbose_name = "Nhân viên"
        verbose_name_plural = "Nhân viên"
        
    def __str__(self):
        return self.user.get_full_name() or self.user.username
        
    def has_permission(self, permission_code):
        """Kiểm tra người dùng có quyền với mã code đã cho không"""
        if not self.role:
            return False
        
        return Permission.objects.filter(
            role_permissions__role=self.role,
            code=permission_code
        ).exists()
    
    def has_permissions(self, permission_codes):
        """Kiểm tra người dùng có tất cả các quyền được chỉ định hay không"""
        if not self.role:
            return False
        
        # Đếm số lượng quyền thỏa điều kiện
        count = Permission.objects.filter(
            role_permissions__role=self.role,
            code__in=permission_codes
        ).count()
        
        # Trả về True nếu có đủ tất cả quyền
        return count == len(permission_codes)
    
    def has_any_permission(self, permission_codes):
        """Kiểm tra người dùng có bất kỳ quyền nào trong danh sách"""
        if not self.role:
            return False
        
        return Permission.objects.filter(
            role_permissions__role=self.role,
            code__in=permission_codes
        ).exists() 