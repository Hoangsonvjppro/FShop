import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fshop.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Role, Employee

# Thông tin tài khoản
username = 'super'
email = 'super@gmail.com'
password = '123'
phone = '0934191038'

# Tạo User hoặc cập nhật nếu đã tồn tại
try:
    user = User.objects.get(username=username)
    print(f"User {username} đã tồn tại, đang cập nhật...")
    user.set_password(password)
    user.email = email
    user.save()
except User.DoesNotExist:
    print(f"Đang tạo User {username}...")
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    print(f"Đã tạo User {username} thành công!")

# Tạo Role 'Admin' nếu chưa tồn tại
role, created = Role.objects.get_or_create(name="Admin")
if created:
    print("Đã tạo Role 'Admin' mới")
else:
    print("Đã tìm thấy Role 'Admin' hiện có")

# Liên kết User với Employee và gán Role
try:
    employee = Employee.objects.get(user=user)
    print(f"Employee cho User {username} đã tồn tại, đang cập nhật...")
    employee.role = role
    employee.phone = phone
    employee.save()
except Employee.DoesNotExist:
    print(f"Đang tạo Employee cho User {username}...")
    employee = Employee.objects.create(
        user=user,
        role=role,
        phone=phone
    )
    print(f"Đã tạo Employee cho User {username} thành công!")

print(f"\n--- HOÀN THÀNH ---")
print(f"Tài khoản {username} đã được thiết lập với quyền admin-panel")
print(f"Username: {username}")
print(f"Password: {password}")
print(f"Email: {email}")
print(f"Số điện thoại: {phone}") 