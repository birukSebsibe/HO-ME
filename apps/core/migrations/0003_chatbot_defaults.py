"""Seed the floating chatbot with a few pre-defined Q&A entries (English source)."""
from django.db import migrations


ENTRIES = [
    {
        "order": 1,
        "question": "What is HO-ME?",
        "answer": "HO-ME (Horn of Africa Missions Engagers) is a faith-based missions movement mobilizing, catalyzing, multiplying and sustaining gospel movements among the unreached peoples of the Horn of Africa.",
        "keywords": "who, about, ho-me, home, mission, what is",
    },
    {
        "order": 2,
        "question": "Where do you work?",
        "answer": "We work across regions and training hubs of the Horn of Africa. See the 'Where We Work' page for the live region list and the interactive map.",
        "keywords": "where, region, hub, location, map, countryside",
    },
    {
        "order": 3,
        "question": "How can I give?",
        "answer": "Visit the Get Involved page and open the Give card to see our giving channels (bank transfer, mobile money, in-kind and online). For receipts and questions email info@ho-me.org.",
        "keywords": "give, giving, donate, donation, money, bank, support, fund",
    },
    {
        "order": 4,
        "question": "How can my church partner with you?",
        "answer": "Churches can adopt an unreached people group, send vetted planters, pray and give together. Open the 'Church Partnership' card on the Get Involved page to apply.",
        "keywords": "church, partner, partnership, congregation, adopt, synod",
    },
    {
        "order": 5,
        "question": "How do I volunteer or apply for staff?",
        "answer": "We welcome volunteers and staff in training, administration, media, and field logistics. Open the 'Volunteer / Staff' card on the Get Involved page to apply.",
        "keywords": "volunteer, staff, serve, apply, work, join, job, career",
    },
    {
        "order": 6,
        "question": "What is Vision 100DM35?",
        "answer": "Vision 100DM35 (2026–2030) is our strategic plan: 100 Disciple-Making Moments by 2035, tracked by live MEL indicators on the Vision page.",
        "keywords": "vision, 100dm35, strategic, plan, target, goal, mel",
    },
    {
        "order": 7,
        "question": "How can I pray for you?",
        "answer": "Join the prayer watch to receive weekly or monthly prayer points for the peoples and hubs of the Horn. Open the 'Prayer Shield' card on the Get Involved page.",
        "keywords": "pray, prayer, intercede, intercession, weekly",
    },
    {
        "order": 8,
        "question": "How do I contact you?",
        "answer": "Email info@ho-me.org or call +251 911 000 000. Our office is in Addis Ababa, Ethiopia.",
        "keywords": "contact, email, phone, address, call, abi, office",
    },
]


def seed(apps, schema_editor):
    ChatbotEntry = apps.get_model("core", "ChatbotEntry")
    if not ChatbotEntry.objects.exists():
        for e in ENTRIES:
            ChatbotEntry.objects.create(**e)


def unseed(apps, schema_editor):
    ChatbotEntry = apps.get_model("core", "ChatbotEntry")
    ChatbotEntry.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_chatbotentry"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
