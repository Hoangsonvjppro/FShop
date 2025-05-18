from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_list_by_category', args=[self.slug])


class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên thương hiệu")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Thương hiệu"
        verbose_name_plural = "Thương hiệu"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    ROOM_CHOICES = (
        ('LR', 'Phòng khách'),
        ('BR', 'Phòng ngủ'),
        ('KT', 'Nhà bếp'),
        ('DR', 'Phòng ăn'),
        ('OF', 'Văn phòng'),
        ('BT', 'Phòng tắm'),
        ('OT', 'Khác'),
    )
    
    MATERIAL_CHOICES = (
        ('WD', 'Gỗ'),
        ('MT', 'Kim loại'),
        ('GL', 'Kính'),
        ('PL', 'Nhựa'),
        ('FB', 'Vải'),
        ('LT', 'Da'),
        ('OT', 'Khác'),
    )
    
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Danh mục")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', verbose_name="Thương hiệu")
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, verbose_name="Hình ảnh")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá bán")
    stock = models.PositiveIntegerField(default=0, verbose_name="Số lượng tồn kho")
    available = models.BooleanField(default=True, verbose_name="Còn hàng")
    room_type = models.CharField(max_length=2, choices=ROOM_CHOICES, default='LR', verbose_name="Loại phòng")
    material = models.CharField(max_length=2, choices=MATERIAL_CHOICES, default='WD', verbose_name="Chất liệu")
    dimensions = models.CharField(max_length=100, blank=True, verbose_name="Kích thước (DxRxC cm)")
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Trọng lượng (kg)")
    warranty = models.PositiveIntegerField(default=12, verbose_name="Bảo hành (tháng)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    is_deleted = models.BooleanField(default=False, verbose_name="Đã xóa")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id', 'slug'])
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id, self.slug])
        
    def get_available_quantity(self):
        return self.stock if self.available else 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Sản phẩm")
    image = models.ImageField(upload_to='products/%Y/%m/%d', verbose_name="Hình ảnh")
    is_main = models.BooleanField(default=False, verbose_name="Ảnh chính")
    
    class Meta:
        verbose_name = "Hình ảnh sản phẩm"
        verbose_name_plural = "Hình ảnh sản phẩm"
        
    def __str__(self):
        return f"Ảnh của {self.product.name}"


class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên nhà cung cấp")
    contact_info = models.CharField(max_length=200, blank=True, verbose_name="Thông tin liên hệ")
    address = models.CharField(max_length=255, blank=True, verbose_name="Địa chỉ")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")

    class Meta:
        verbose_name = "Nhà cung cấp"
        verbose_name_plural = "Nhà cung cấp"
        ordering = ['name']

    def __str__(self):
        return self.name


class Import(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='imports', verbose_name="Nhà cung cấp")
    employee = models.ForeignKey('accounts.Employee', on_delete=models.CASCADE, related_name='imports', verbose_name="Nhân viên")
    import_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày nhập")
    total = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Tổng tiền")
    note = models.TextField(blank=True, verbose_name="Ghi chú")

    class Meta:
        verbose_name = "Phiếu nhập"
        verbose_name_plural = "Phiếu nhập"
        ordering = ['-import_date']

    def __str__(self):
        return f"Phiếu nhập #{self.id} - {self.import_date.strftime('%d/%m/%Y')}"


class ImportDetail(models.Model):
    import_obj = models.ForeignKey(Import, on_delete=models.CASCADE, related_name='details', verbose_name="Phiếu nhập")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='import_details', verbose_name="Sản phẩm")
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    unit_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Đơn giá")
    
    class Meta:
        verbose_name = "Chi tiết phiếu nhập"
        verbose_name_plural = "Chi tiết phiếu nhập"
        
    def __str__(self):
        return f"Chi tiết phiếu nhập #{self.import_obj.id} - {self.product.name}"
        
    @property
    def subtotal(self):
        return self.quantity * self.unit_price 