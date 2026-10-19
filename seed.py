"""
HO-ME seed script — populates the CMS with realistic initial sample data.

Usage (from project root):
    ./.venv/Scripts/python manage.py shell < seed.py
    # or: make it idempotent and run repeatedly — safe to re-run.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

from apps.core.models import (
    CoreValue, LeadershipProfile, PartnerLogo, SiteSetting, TimelineMilestone,
)
from apps.cms_content.models import (
    DmmGenerationStep, DigitalMinistrySummary, KingdomBusinessIga, McmsStep,
    MelIndicator, Pillar, RegionHub, Story, TrainingProgram,
)
from apps.resources.models import Language, Resource, ResourceCategory, TargetAudience
from apps.accounts.models import GivingOption

User = get_user_model()


def l(model, defaults, lookup=None):
    """Idempotent get_or_create helper."""
    lookup = lookup or {k: v for k, v in defaults.items() if isinstance(k, str)}
    obj, created = model.objects.get_or_create(defaults=defaults, **{k: v for k, v in lookup.items()})
    return obj, created


# ---------------------------------------------------------------------------
# Site settings singleton + counters + hero
# ---------------------------------------------------------------------------
site, _ = SiteSetting.objects.get_or_create(
    pk=1,
    defaults=dict(
        hero_variant="A",
        headline_a="Reaching the Unreached of the Horn of Africa",
        headline_b="Every Unreached People. Every Generation. Every Nation — by 2035.",
        subheadline="HO-ME mobilizes, catalyzes, multiplies and sustains gospel movements "
                    "among the unreached peoples of the Horn of Africa.",
    ),
)
# Counters (update each run to stay authoritative)
site.counter_churches = site.counter_churches or 23000
site.counter_years = site.counter_years or 20
site.counter_upgs = site.counter_upgs or 8
site.counter_hubs = site.counter_hubs or 10
site.counter_network = site.counter_network or 4000
site.save()

# ---------------------------------------------------------------------------
# Timeline 2003 → 2030
# ---------------------------------------------------------------------------
TIMELINE = [
    (2003, "Vision born in prayer", "A small prayer circle asks God for the unreached peoples of the Horn.", "flame"),
    (2005, "First HOST school cohort", "12 workers trained in cross-cultural ministry & DMM.", "graduation-cap"),
    (2008, "Tigray engagement begins", "First long-term team deploys to Tigray region.", "map-pin"),
    (2011, "Gondar & Arsi hubs open", "Regional training hubs multiply the HOST model.", "map-pin"),
    (2015, "1,000 churches milestone", "Networked churches pass 1,000 across three regions.", "church"),
    (2018, "Kingdom business IGAs", "Marketplace ministry funds local sustainability.", "briefcase"),
    (2020, "Digital ministry pivot", "Online discipleship reaches unreached diaspora & remote areas.", "smartphone"),
    (2023, "Vision 100DM35 launched", "100 disciple-making movements across 35 UPGs by 2035.", "rocket"),
    (2025, "23,000+ churches networked", "HO-ME networks over 23,000 churches in 8 UPGs.", "network"),
    (2027, "8–12 hubs operational", "Every active UPG maps to a staging hub.", "landmark"),
    (2030, "TARGET: self-sustaining movements", "Indigenous, multiplying, reproducing movements in every engaged UPG.", "target"),
]
for year, title, desc, icon in TIMELINE:
    TimelineMilestone.objects.get_or_create(site=site, year=year, defaults=dict(title=title, description=desc, icon=icon))

# ---------------------------------------------------------------------------
# Core values (4 cards)
# ---------------------------------------------------------------------------
VALUES = [
    (1, "Prayer-Powered", "Everything begins and continues on our knees.", "hand-heart"),
    (2, "Locally Led", "Indigenous leaders own every movement we catalyze.", "users"),
    (3, "Multiplication-Minded", "We plant movements, not just churches.", "sprout"),
    (4, "Accountable Stewardship", "Measured, transparent, MEL-driven.", "scale"),
]
for n, title, body, icon in VALUES:
    CoreValue.objects.get_or_create(site=site, number=n, defaults=dict(title=title, body=body, icon=icon))

# ---------------------------------------------------------------------------
# Leadership profiles
# ---------------------------------------------------------------------------
LEADERS = [
    ("Dr. Abdullahi Girma", "Executive Director", "20+ years of frontier missions leadership across the Horn."),
    ("Meseret Haile", "Director of Training (HOST)", "Leads the HOST school and regional hub curriculum."),
    ("Fatuma Ali", "Regional Coordinator — Somali", "Oversees engagement among Somali UPGs."),
    ("Yonas Tesfaye", "MEL Lead (Vision 100DM35)", "Champions measurement, evaluation & learning."),
]
for name, role, bio in LEADERS:
    LeadershipProfile.objects.get_or_create(site=site, name=name, defaults=dict(role=role, bio=bio))

# Partner logos (text-only placeholders until logos uploaded)
for partner in ("ECGBC", "SIM Partner Network", "Hub Partners Alliance"):
    PartnerLogo.objects.get_or_create(site=site, name=partner)

# ---------------------------------------------------------------------------
# MCMS cycle
# ---------------------------------------------------------------------------
MCMS = [
    ("mobilize", "Mobilize", "megaphone", "Awaken churches & believers to the unreached.", "Casting vision in partner churches, prayer networks and youth movements until every member is a missions engager."),
    ("catalyze", "Catalyze", "zap", "Spark disciple-making through HOST schools & teams.", "Deploying trained catalytic teams that launch reproducing Bible studies among the unreached."),
    ("multiply", "Multiply", "network", "Reproduce generations of disciples & churches.", "Every disciple multiplies — gen 1 → gen 4 and beyond, until movements are self-reproducing."),
    ("sustain", "Sustain", "shield", "Sustain with IGAs, hubs, and MEL rigor.", "Kingdom business, regional hubs and disciplined measurement keep movements healthy long-term."),
]
for key, name, icon, short, desc in MCMS:
    McmsStep.objects.get_or_create(key=key, defaults=dict(name=name, icon=icon, short_line=short, description=desc, order=len(key)))

# ---------------------------------------------------------------------------
# Pillars
# ---------------------------------------------------------------------------
PILLARS = [
    (1, "Prayer & Spiritual Warfare", "Intercession networks covering every UPG.", "hand-heart"),
    (2, "Training & HOST Schools", "Equipping catalytic workers for frontier ministry.", "graduation-cap"),
    (3, "Church Planting & DMM", "Multiplying disciples, groups and churches.", "church"),
    (4, "Kingdom Business & Digital", "Sustainable IGA + online ministry innovation.", "briefcase"),
]
for n, title, summary, icon in PILLARS:
    Pillar.objects.get_or_create(number=n, defaults=dict(title=title, summary=summary, icon=icon))

# ---------------------------------------------------------------------------
# DMM generations
# ---------------------------------------------------------------------------
GENS = [
    (1, "Share & Pray", "Believers share Christ with proximity & prayer."),
    (2, "Disciple Groups", "New believers gather into discovery Bible groups."),
    (3, "Leaders Emerge", "Group leaders coach the next generation."),
    (4, "Churches Multiply", "Groups become reproducing churches planting again."),
]
for n, title, desc in GENS:
    DmmGenerationStep.objects.get_or_create(number=n, defaults=dict(title=title, description=desc, icon="chevron-right"))

# ---------------------------------------------------------------------------
# HOST programs & fees
# ---------------------------------------------------------------------------
host, _ = TrainingProgram.objects.get_or_create(
    slug="host-frontier-missions",
    defaults=dict(
        name="HOST Frontier Missions School",
        kind="HOST School",
        duration="12 weeks residential + 6-month field practicum",
        overview="Holistic training in cross-cultural ministry, DMM strategy, language acquisition & Kingdom business.",
        fee_rows=[
            {"label": "Tuition (national staff)", "amount": "ETB 12,000"},
            {"label": "Tuition (international)", "amount": "USD 600"},
            {"label": "Room & board", "amount": "ETB 6,000"},
            {"label": "Field practicum travel", "amount": "Subsidized"},
        ],
        icon="graduation-cap",
    ),
)
TrainingProgram.objects.get_or_create(
    slug="host-online-dmm-basics",
    defaults=dict(
        name="HOST Online: DMM Basics",
        kind="Online course",
        duration="6 weeks self-paced",
        overview="Digital-first intro to disciple-making movements for diaspora and partner churches.",
        fee_rows=[{"label": "Course fee", "amount": "Free (donation welcome)"}],
        icon="monitor",
    ),
)

# ---------------------------------------------------------------------------
# Kingdom business IGAs
# ---------------------------------------------------------------------------
IGAS = [
    ("Beekeeping Cooperatives", "Honey value-chains fund local workers.", "hexagon"),
    ("Grain & Milling", "Grain trading stabilizes family income.", "wheat"),
    ("Solar Installation", "Off-grid business serving rural communities.", "sun"),
]
for title, summary, icon in IGAS:
    KingdomBusinessIga.objects.get_or_create(title=title, defaults=dict(summary=summary, icon=icon))

DigitalMinistrySummary.objects.get_or_create(pk=1, defaults=dict(
    heading="Digital Ministry",
    body="Encrypted livestreams, WhatsApp discipleship pods and mobile micro-courses reach remote and diaspora unreached communities safely.",
    cta_text="Explore digital training",
    cta_url="/library/",
))

# ---------------------------------------------------------------------------
# Regions & hubs
# ---------------------------------------------------------------------------
REGIONS = [
    ("Tigray", "region", 2, 8200, "engaged", 13.6, 39.5,
     "Long-term engagement among the Irob & Saho peoples; two training hubs active."),
    ("Gondar", "region", 1, 4100, "engaged", 12.6, 37.4,
     "Amhara-dominant zone with emerging engagement of the Kemant people."),
    ("Arsi", "region", 1, 3900, "emerging", 7.9, 39.2,
     "Oromo-Arsi UPG engagement with growing church network."),
    ("Somali", "region", 2, 5600, "pioneering", 6.5, 44.0,
     "Frontier engagement among Somali clans; pioneering phase."),
    ("Afar", "region", 1, 1800, "vision", 11.8, 40.9,
     "Vision-stage engagement with the Afar people."),
    ("Addis Ababa Hub", "hub", 1, 9000, "engaged", 9.0, 38.7,
     "Central logistics, HOST school HQ and diaspora mobilization hub."),
]
for name, rtype, upgs, churches, status, lat, lon, summary in REGIONS:
    RegionHub.objects.get_or_create(
        name=name,
        defaults=dict(region_type=rtype, upg_count=upgs, total_churches=churches,
                      status=status, summary=summary, latitude=lat, longitude=lon,
                      pin_label=name),
    )

# ---------------------------------------------------------------------------
# Vision 100DM35 MEL indicators
# ---------------------------------------------------------------------------
INDICATORS = [
    ("V1.1", "Engaged UPGs", "count", "increase", 8, 8, 35, "Movement"),
    ("V1.2", "4th-generation DMM movements", "count", "increase", 2, 3, 100, "Movement"),
    ("V2.1", "HOST graduates deployed", "persons", "increase", 240, 297, 1000, "Training"),
    ("V2.2", "Active training hubs", "count", "increase", 6, 7, 12, "Training"),
    ("V3.1", "Networked churches", "count", "increase", 23100, 23480, 40000, "Network"),
    ("V3.2", "Kingdom business IGAs operating", "count", "increase", 9, 11, 30, "Sustainability"),
    ("V4.1", "Local giving % of budget", "percent", "increase", 18, 22, 60, "Sustainability"),
    ("V4.2", "Prayer network members", "persons", "increase", 5200, 6100, 25000, "Prayer"),
]
for code, name, unit, direction, base, cur, tgt, pillar in INDICATORS:
    MelIndicator.objects.get_or_create(
        code=code,
        defaults=dict(name=name, unit=unit, direction=direction, baseline_2025=base,
                      current_value=cur, target_2030=tgt, pillar=pillar),
    )

# ---------------------------------------------------------------------------
# Impact & stories (safety-approved defaults for demo)
# ---------------------------------------------------------------------------
STORIES = [
    ("story", "A church is born in the Afar lowlands", "After two years of prayer-walking, the first house church gathers.",
     "Twelve believers now meet weekly in the Afar lowlands — the fruit of a two-year prayer-walking effort by the Gondar hub team. A 4th-generation group is already forming.", True, "Afar"),
    ("testimony", "“I met Jesus through a WhatsApp group”", "A diaspora testimony of digital discipleship.",
     "Growing up in a Muslim-majority village there was no church for 300 km. A WhatsApp discovery group shared the gospel; today Ahmed leads two online groups back home.", True, "Somali"),
    ("news", "HOST school opens 2026 cohort applications", "Applications open for residential & online tracks.",
     "The Frontier Missions School invites applications for its 2026 cohort — 12 weeks residential, 6-month field practicum among an unreached people. Fees & forms available in the resource library.", True, None),
    ("story", "Beekeeping funds a new hub", "IGA profits financed the Arsi staging hub.",
     "The Arsi beekeeping cooperative's year-one profits paid the deposit on the region's staging hub — local sustainability in action.", False, "Arsi"),
]
for kind, title, excerpt, body, featured, region_name in STORIES:
    region = RegionHub.objects.filter(name=region_name).first() if region_name else None
    Story.objects.get_or_create(
        title=title,
        defaults=dict(kind=kind, excerpt=excerpt, body=f"<p>{body}</p>",
                      safety_review_status="approved", is_featured=featured,
                      region=region, tags="HO-ME, DMM"),
    )

# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------
cat_train, _ = ResourceCategory.objects.get_or_create(name="Training", defaults=dict(slug="training", order=1))
cat_mel, _ = ResourceCategory.objects.get_or_create(name="MEL & Research", defaults=dict(slug="mel-research", order=2))
cat_pray, _ = ResourceCategory.objects.get_or_create(name="Prayer", defaults=dict(slug="prayer", order=3))
en, _ = Language.objects.get_or_create(name="English", defaults=dict(code="en"))
am, _ = Language.objects.get_or_create(name="Amharic", defaults=dict(code="am"))
so, _ = Language.objects.get_or_create(name="Somali", defaults=dict(code="so"))
aud_all, _ = TargetAudience.objects.get_or_create(name="Everyone")
aud_lead, _ = TargetAudience.objects.get_or_create(name="Church leaders")
aud_staff, _ = TargetAudience.objects.get_or_create(name="HO-ME staff")

if not Resource.objects.exists():
    r1, _ = Resource.objects.get_or_create(title="Weekly Prayer Guide (sample)", defaults=dict(
        description="Scripture-based weekly guide for the 8 engaged UPGs.", category=cat_pray, language=en,
        visibility="public", external_url="https://example.com"))
    r1.audiences.set([aud_all])
    r2, _ = Resource.objects.get_or_create(title="Vision 100DM35 Framework (PDF)", defaults=dict(
        description="Full MEL framework, indicators & governance.", category=cat_mel, language=en,
        visibility="request"))
    r2.audiences.set([aud_lead, aud_staff])

# ---------------------------------------------------------------------------
# Giving options
# ---------------------------------------------------------------------------
GivingOption.objects.get_or_create(kind="bank", title="Bank Transfer (Ethiopia)", defaults=dict(
    details="Commercial Bank of Ethiopia\nAcct: 1000XXXXXXX\nSWIFT: CBETETAA\nBranch: Addis Ababa Main"))
GivingOption.objects.get_or_create(kind="mobile", title="Mobile Money", defaults=dict(
    details="Telebirr: +251 9XX XXX XXX\nM-Pesa (Kenya): +254 7XX XXX XXX"))
GivingOption.objects.get_or_create(kind="inkind", title="In-Kind & Services", defaults=dict(
    details="Gifts of grain, solar kits, printing or professional services — contact the office."))

# ---------------------------------------------------------------------------
# Initial admin user (username + password only)
# ---------------------------------------------------------------------------
if not User.objects.filter(username="admin").exists():
    # Override via env (DJANGO_ADMIN_PASSWORD). Stored in ADMIN_CREDENTIALS.txt.
    ADMIN_PASSWORD = os.environ.get("DJANGO_ADMIN_PASSWORD", "HOME-Tf8OJP9M9n-Ax9!")
    User.objects.create_superuser(
        "admin", "admin@ho-me.org", ADMIN_PASSWORD, job_title="Portal Administrator", is_mel_admin=True,
    )
    print(f"Created superuser: admin / {ADMIN_PASSWORD}")
else:
    print("- admin user already exists (password unchanged)")

print("Seed complete.")
