from django import template

register = template.Library()

@register.filter
def abs_value(value):
    """Trả về giá trị tuyệt đối của một số."""
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value

@register.filter
def has_perm(employee, permission_code):
    """Kiểm tra xem nhân viên có quyền không."""
    if not employee or not hasattr(employee, 'has_permission'):
        return False
    return employee.has_permission(permission_code)

@register.filter
def has_any_perm(employee, permission_codes):
    """Kiểm tra xem nhân viên có ít nhất một quyền trong danh sách."""
    if not employee or not hasattr(employee, 'has_any_permission'):
        return False
    
    codes = permission_codes.split(',')
    return employee.has_any_permission(codes)

@register.filter
def currency_format(value):
    """Định dạng số tiền theo chuẩn tiền tệ Việt Nam."""
    try:
        # Chuyển đổi thành số nếu là chuỗi
        if isinstance(value, str):
            value = float(value.replace(',', ''))
            
        # Trả về số được định dạng với dấu phân cách hàng nghìn
        # và không có thập phân (làm tròn thành số nguyên)
        return "{:,.0f}".format(value)
    except (ValueError, TypeError):
        return value 