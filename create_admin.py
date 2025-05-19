#!/usr/bin/env python
import os
import sys
import django

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fshop.settings')

# Initialize Django
django.setup()

from django.contrib.auth.models import User
from accounts.models import Employee, Role, Permission, RolePermission
from admin_panel.views import create_default_permissions


def create_superuser():
    """
    Tạo tài khoản admin (superuser)
    """
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123456'
    
    # Kiểm tra xem superuser đã tồn tại chưa
    if not User.objects.filter(username=username).exists():
        print(f"Tạo tài khoản superuser: {username}")
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Tạo các quyền mặc định
        print("Khởi tạo quyền mặc định và vai trò...")
        create_default_permissions()
        
        # Gán vai trò admin cho superuser
        admin_role = Role.objects.get(name="Admin")
        Employee.objects.create(
            user=user,
            role=admin_role,
            phone='0123456789',
            address='Admin address'
        )
        
        print("Tài khoản superuser đã được tạo thành công!")
        print(f"Username: {username}")
        print(f"Password: {password}")
    else:
        print(f"Superuser {username} đã tồn tại.")
        
        # Vẫn tạo các quyền mặc định nếu chưa có
        print("Kiểm tra và tạo quyền mặc định nếu cần...")
        create_default_permissions()


def create_sudo_user():
    """
    Tạo tài khoản sudo với đầy đủ quyền truy cập
    """
    username = 'sudo'
    email = 'sudo@example.com'
    password = '123'
    
    # Kiểm tra xem sudo user đã tồn tại chưa
    if not User.objects.filter(username=username).exists():
        print(f"Tạo tài khoản sudo: {username}")
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Đảm bảo các quyền mặc định đã được tạo
        create_default_permissions()
        
        # Gán vai trò admin cho sudo user
        admin_role = Role.objects.get(name="Admin")
        Employee.objects.create(
            user=user,
            role=admin_role,
            phone='0987654321',
            address='Sudo address'
        )
        
        print("Tài khoản sudo đã được tạo thành công!")
        print(f"Username: {username}")
        print(f"Password: {password}")
    else:
        print(f"Sudo user {username} đã tồn tại.")


if __name__ == '__main__':
    create_superuser()
    create_sudo_user() 