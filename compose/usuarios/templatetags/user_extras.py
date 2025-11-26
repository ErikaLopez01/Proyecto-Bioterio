from django import template

register = template.Library()

@register.filter(name="has_group")
def has_group(user, group_name: str) -> bool:
    """Devuelve True si el usuario pertenece al grupo indicado."""
    if user.is_anonymous:
        return False
    return user.groups.filter(name=group_name).exists()
