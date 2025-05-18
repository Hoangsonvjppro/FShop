from django import template

register = template.Library()

@register.filter
def abs_value(value):
    """Trả về giá trị tuyệt đối của một số."""
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value 