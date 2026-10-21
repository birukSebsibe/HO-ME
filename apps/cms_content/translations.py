"""
Whole-site content translation.

A registry of admin-editable CMS text fields that can hold per-language
overrides (Amharic / Afaan Oromoo), backed by cms_content.ContentTranslation.
`resolve` is what templates use (via the `tfield` filter and SiteSetting
computed in Python); it falls back to the original value when no override
exists for the active language.
"""

from django.db.models import Q
from django.utils.translation import get_language

from .models import ContentTranslation

from apps.cms_content.models import (
    DmmGenerationStep,
    DigitalMinistrySummary,
    KingdomBusinessIga,
    McmsStep,
    MelIndicator,
    Pillar,
    RegionHub,
    Story,
    TrainingProgram,
)
from apps.core.models import (
    ChatbotEntry,
    CoreValue,
    LeadershipProfile,
    SiteSetting,
    TimelineMilestone,
)
from apps.accounts.models import GivingOption

# ---------------------------------------------------------------------------
# Registry: which model fields can be overridden per language
# (model class, human label, field name). Pages read these through tfield.
# ---------------------------------------------------------------------------

TRANSLATABLE = (
    # (model class, [field names], admin-facing label)
    (SiteSetting, ["site_tagline", "headline_a", "headline_b", "subheadline",
                   "hero_cta_text_1", "hero_cta_text_2", "footer_note"], "Site Settings"),
    (Pillar, ["title", "summary"], "Ministry Pillars"),
    (McmsStep, ["name", "short_line", "description"], "MCMS Steps"),
    (DmmGenerationStep, ["title", "description"], "DMM Generations"),
    (TrainingProgram, ["name", "overview", "duration"], "Training Programs"),
    (KingdomBusinessIga, ["title", "summary"], "Kingdom Business IGAs"),
    (DigitalMinistrySummary, ["heading", "body", "cta_text"], "Digital Ministry"),
    (RegionHub, ["name", "summary"], "Regions & Hubs"),
    (MelIndicator, ["name", "pillar", "notes"], "MEL Indicators"),
    (Story, ["title", "excerpt", "body"], "Stories"),
    (CoreValue, ["title", "body"], "Core Values"),
    (TimelineMilestone, ["title", "description"], "Timeline Milestones"),
    (LeadershipProfile, ["role", "bio"], "Leadership Profiles"),
    (ChatbotEntry, ["question", "answer", "keywords"], "Chatbot Q&A"),
    (GivingOption, ["title", "details"], "Giving Options"),
)


def registry_rows():
    """Yield (model, model_label, field) tuples for the admin manager page."""
    for model, fields, label in TRANSLATABLE:
        for f in fields:
            yield model, label, f


_TRANSLATABLE_LOOKUP = {
    (model.__name__.lower(), f): True
    for model, fields, _label in TRANSLATABLE
    for f in fields
}


def is_translatable(model, field_name: str) -> bool:
    return _TRANSLATABLE_LOOKUP.get((model.__name__.lower(), field_name), False)


# ---------------------------------------------------------------------------
# Runtime resolution with per-request caching
# ---------------------------------------------------------------------------

_cache = {}  # lang -> {model_name: {pk: {field: text}}}


def _invalidate(sender=None, **kwargs):
    _cache.clear()


from django.db.models.signals import post_delete, post_save  # noqa: E402

post_save.connect(_invalidate, sender=ContentTranslation)
post_delete.connect(_invalidate, sender=ContentTranslation)


def _load(lang: str):
    """Load every override for a language into a nested dict (once per request)."""
    if lang in _cache:
        return _cache[lang]
    data = {}
    for t in ContentTranslation.objects.filter(language=lang).select_related("content_type"):
        data.setdefault(t.content_type.model.lower(), {}).setdefault(t.object_id, {})[t.field_name] = t.text
    _cache[lang] = data
    return data


def resolve(obj, field_name: str, default=None):
    """Return the override for the active language, falling back to the field value."""
    if obj is None:
        return default
    if not is_translatable(type(obj), field_name):
        return getattr(obj, field_name, default)
    overridden = _load(get_language() or "en")
    model_data = overridden.get(type(obj).__name__.lower(), {}).get(obj.pk)
    if model_data and field_name in model_data and str(model_data[field_name]).strip():
        return model_data[field_name]
    return getattr(obj, field_name, default)
