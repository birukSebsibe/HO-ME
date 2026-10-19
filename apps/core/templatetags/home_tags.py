from django import template

register = template.Library()


@register.filter
def commas(value):
    """Render 23000 as 23,000."""
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return value


@register.filter
def plus(value):
    try:
        return f"{int(value):,}+"
    except (TypeError, ValueError):
        return value
