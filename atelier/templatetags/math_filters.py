from django import template

register = template.Library()

@register.filter
def div(value, arg):
    """Делит значение на аргумент"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def mul(value, arg):
    """Умножает значение на аргумент"""
    try:
        return float(value) * float(arg)
    except (ValueError, ZeroDivisionError):
        return None
    
@register.filter
def subtract(value, arg):
    """Вычитает arg из value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0    