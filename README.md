# FShop - Website Bán Nội Thất

![FShop Logo](https://via.placeholder.com/150x50?text=FShop)

FShop là một website hiện đại về bán nội thất được phát triển bằng Django. Dự án này cung cấp đầy đủ tính năng cần thiết cho một cửa hàng trực tuyến, từ quản lý sản phẩm, người dùng đến xử lý đơn hàng.

## Tính Năng Chính

### Người Dùng
- Đăng ký, đăng nhập và quản lý tài khoản
- Xem và tìm kiếm sản phẩm theo danh mục, thương hiệu
- Thêm sản phẩm vào giỏ hàng
- Quản lý giỏ hàng (thêm, xóa, cập nhật số lượng)
- Đặt hàng và theo dõi trạng thái đơn hàng
- Quản lý địa chỉ giao hàng

### Quản Trị Viên
- Dashboard với thống kê và báo cáo tổng quan
- Quản lý sản phẩm, danh mục, thương hiệu
- Xử lý đơn hàng (xác nhận, cập nhật trạng thái)
- Quản lý người dùng
- Quản lý nhà cung cấp và nhập hàng
- Quản lý hình ảnh sản phẩm (nhiều ảnh cho mỗi sản phẩm)

## Công Nghệ Sử Dụng

- **Backend**: Django
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Database**: SQLite (phát triển), PostgreSQL (khuyến nghị cho production)
- **Authentication**: Django Authentication System, django-allauth
- **Forms**: django-crispy-forms với crispy-tailwind
- **Media**: Pillow cho xử lý hình ảnh
- **Environment**: python-decouple, python-dotenv

## Cài Đặt

### Yêu Cầu
- Python 3.8+
- pip

### Các Bước Cài Đặt

1. Clone repository:
```
git clone https://github.com/yourusername/fshop.git
cd FShop
```

2. Tạo và kích hoạt môi trường ảo:
```
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
```

3. Cài đặt các thư viện:
```
pip install -r requirements.txt
```

4. Tạo file .env trong thư mục gốc và thiết lập các biến môi trường:
```
SECRET_KEY=your_secret_key
DEBUG=True
```

5. Thực hiện migrate để tạo cơ sở dữ liệu:
```
python manage.py migrate
```

6. Tạo tài khoản admin:
```
python manage.py createsuperuser
```

7. Chạy server phát triển:
```
python manage.py runserver
```

8. Truy cập website tại http://127.0.0.1:8000 và trang admin tại http://127.0.0.1:8000/admin

## Cấu Trúc Dự Án

```
FShop/
├── accounts/            # Quản lý người dùng, địa chỉ, phân quyền
├── admin_panel/         # Giao diện quản trị viên
├── cart/                # Quản lý giỏ hàng, sản phẩm đã lưu
├── fshop/               # Cấu hình dự án Django chính
├── media/               # Lưu trữ hình ảnh, file tải lên
├── orders/              # Quản lý đơn hàng, chi tiết đơn hàng
├── products/            # Quản lý sản phẩm, danh mục, thương hiệu, ảnh
├── static/              # CSS, JavaScript, hình ảnh tĩnh
├── templates/           # Templates HTML
├── manage.py            # Tập lệnh quản lý Django
└── requirements.txt     # Danh sách thư viện cần thiết
```

## Mô Hình Dữ Liệu

### Products
- Category: Danh mục sản phẩm
- Brand: Thương hiệu
- Product: Thông tin sản phẩm (tên, mô tả, giá, tồn kho, loại phòng, chất liệu)
- ProductImage: Quản lý nhiều hình ảnh cho mỗi sản phẩm
- Supplier: Nhà cung cấp
- Import/ImportDetail: Quản lý nhập hàng

### Accounts
- User: Thông tin người dùng, phân quyền
- Address: Địa chỉ giao hàng

### Cart
- Cart: Giỏ hàng của người dùng
- CartItem: Sản phẩm trong giỏ hàng
- SavedItem: Sản phẩm đã lưu để mua sau

### Orders
- Order: Thông tin đơn hàng
- OrderItem: Chi tiết sản phẩm trong đơn hàng
- OrderStatus: Quản lý trạng thái đơn hàng

## Hướng Dẫn Sử Dụng

### Người Dùng
1. Đăng ký tài khoản mới hoặc đăng nhập
2. Duyệt sản phẩm theo danh mục hoặc thương hiệu
3. Thêm sản phẩm vào giỏ hàng
4. Tiến hành thanh toán, cung cấp thông tin giao hàng
5. Theo dõi trạng thái đơn hàng

### Quản Trị Viên
1. Đăng nhập vào trang quản trị
2. Quản lý danh mục và sản phẩm
3. Xử lý đơn hàng, cập nhật trạng thái
4. Theo dõi báo cáo, thống kê

## Phát Triển

### Các Bước Tiếp Theo
- Triển khai tích hợp thanh toán trực tuyến
- Thêm tính năng đánh giá và nhận xét sản phẩm
- Cải thiện hệ thống tìm kiếm và lọc sản phẩm
- Thiết lập hệ thống thông báo qua email
- Tối ưu hiệu suất và SEO

### Đóng Góp
Nếu bạn muốn đóng góp vào dự án, vui lòng tạo pull request hoặc báo cáo các vấn đề trong phần Issues.

## Giấy Phép
[MIT License](LICENSE)

## Liên Hệ
Để biết thêm thông tin, vui lòng liên hệ: support@fshop.com 