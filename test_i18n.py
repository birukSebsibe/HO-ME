"""Throwaway verification of the language-switching feature (en/am/om)."""
from django.test import Client
from django.utils import translation
from django.utils.translation import gettext as _
from apps.core.models import SiteSetting

AM_WHAT_WE_DO = "ምን እንሰራለን"      # What We Do
AM_PRAYER = "ጸሎት"                # Prayer
AM_GET_INVOLVED = "ይሳተፉ"          # Get Involved
AM_USERNAME = "የተጠቃሚ ስም"          # Username
AM_FORGOT = "ረስተዋል"               # Forgot (password)
AM_LOG_OUT = "ውጣ"                 # Log out
AM_DASHBOARD = "ዳሽቦርድ"            # Dashboard

c = Client()
ok = []

def check(name, cond):
    ok.append((name, bool(cond)))
    print(("PASS" if cond else "FAIL") + "  " + name)

# ---------------- Amharic on the public site ----------------
r = c.post("/setlang/", {"language": "am", "next": "/"})
check("POST /setlang/ redirects (am)", r.status_code == 302)
r = c.get("/")
check("home 200 in am", r.status_code == 200)
check("nav rendered in Amharic", AM_WHAT_WE_DO in r.content.decode())
check("English nav hidden", "What We Do" not in r.content.decode())
check("html lang=am", 'lang="am"' in r.content.decode())
check("language switcher present", "Afaan Oromoo" in r.content.decode())

r = c.get("/get-involved/")
check("get-involved 200 in am", r.status_code == 200)
check("tab label ጸሎት (Prayer)", AM_PRAYER in r.content.decode())
check("CTA ይሳተፉ (Get Involved)", AM_GET_INVOLVED in r.content.decode())

# ---------------- Oromifa ----------------
r = c.post("/setlang/", {"language": "om", "next": "/"}, follow=True)
check("switch to om (follow redirect)", r.status_code == 200)
check("nav in Afaan Oromoo", "Wantoota nut dalagnu" in r.content.decode())

# ---------------- Admin portal in Amharic ----------------
c.post("/setlang/", {"language": "am", "next": "/admin-portal/login/"})
r = c.get("/admin-portal/login/")
check("admin login 200 in am", r.status_code == 200)
check("admin login label የተጠቃሚ ስም (Username)", AM_USERNAME in r.content.decode())
check("admin login ረስተዋል link", AM_FORGOT in r.content.decode())

s = SiteSetting.load()
if s.logo:
    check("website logo shown on admin login", str(s.logo.url) in r.content.decode())
else:
    print("NOTE  no logo uploaded yet - card falls back to text heading")

r = c.get("/admin-portal/password-reset/")
check("password-reset page 200 in am", r.status_code == 200)
check("reset page Amharic heading", AM_FORGOT in r.content.decode())

# ---------------- Catalog drives Django admin chrome too ----------------
with translation.override("am"):
    check("admin 'Log out' am", _("Log out") == AM_LOG_OUT)
    check("admin 'Dashboard' am", _("Dashboard") == AM_DASHBOARD)
with translation.override("om"):
    check("admin 'Log out' om", _("Log out") == "Ba'i")
    check("admin 'Save' om", _("Save") == "Olkaa'i")

fails = [n for n, v in ok if not v]
print("SUMMARY: %d/%d passed" % (len(ok) - len(fails), len(ok)))
raise SystemExit(1 if fails else 0)
