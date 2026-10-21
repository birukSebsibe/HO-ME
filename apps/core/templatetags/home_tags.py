from django import template

register = template.Library()


@register.filter
def tfield(obj, field):
    """Return the active-language override for a translatable CMS field.

    Usage: {{ pillar|tfield:"title" }} — falls back to the original value.
    """
    try:
        from apps.cms_content.translations import resolve
        return resolve(obj, field)
    except Exception:
        try:
            return getattr(obj, field)
        except Exception:
            return ""


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
