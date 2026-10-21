from apps.core.models import ChatbotEntry, SiteSetting


def site_settings(request):
    """Global site settings + the active pre-defined chatbot Q&A list."""
    faq = [
        {
            "q": e.question,
            "a": e.answer,
            "kw": [k.strip() for k in e.keywords.split(",") if k.strip()],
        }
        for e in ChatbotEntry.objects.filter(is_active=True).order_by("order", "id")
    ]
    return {"site": SiteSetting.load(), "chatbot_faq": faq}
