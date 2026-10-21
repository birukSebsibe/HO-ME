"""
Build HO-ME's Amharic (am) and Oromifa (Afaan Oromoo, om) translation catalogs.

Usage (from project root):
    ./.venv/Scripts/python locale/build_catalogs.py

Writes locale/<code>/LC_MESSAGES/django.po and compiles django.mo.
Uses polib (pure Python) so no system gettext is required.

Editing workflow: update the TRANSLATIONS table below (or the generated .po
files), then re-run this script. Strings with an empty translation simply
fall back to English.
"""

import sys
from pathlib import Path

import polib

LOCALE_DIR = Path(__file__).resolve().parent

TRANSLATIONS = {
    # ------------------------------------------------------------------
    # msgid: (Amharic, Oromifa/Afaan Oromoo)
    # ------------------------------------------------------------------
    # --- Public site chrome (base.html: nav, footer, CTA) ---
    "About Us": ("ስለ እኛ", "Waa'ee keenya"),
    "What We Do": ("ምን እንሰራለን", "Wantoota nut dalagnu"),
    "Where We Work": ("የምንሰራበት ቦታ", "Bakka nut hojjennu"),
    "Impact & Stories": ("ተጽዕኖ እና ታሪኮች", "Faayidaa fi Seenoota"),
    "Library": ("ቤተ መጻሕፍት", "Maktabaa"),
    "Get Involved": ("ይሳተፉ", "Nu wajjin hirmaadhaa"),
    "Explore": ("ይጎብኙ", "Sakatta'i"),
    "Resources": ("", "Qabeenyoota"),
    "Contact": ("ያግኙን", "Wal qunnamtii"),
    "Privacy Policy": ("", "Karoora Icciitii"),
    "Transparency": ("", "Banamummaa"),
    "Resource Library": ("የመረጃ ቤተ መጻሕፍት", "Kuufama Qabeenyoota"),
    # --- Admin portal: sign-in card ---
    "Horn of Africa Missions Engagers — secure staff sign-in.": (
        "ደህንነቱ የተጠበቀ የሠራተኛ መግቢያ", "Hojjetaa nageenyaan seeni."),
    "Username": ("የተጠቃሚ ስም", "Maqaa fayyadamaa"),
    "Password": ("የይለፍ ቃል", "Jecha icciitii"),
    "Email address": ("የኢሜይል አድራሻ", "Teessoo iimeelii"),
    "Sign in": ("ይግቡ", "Seeni"),
    "Sign in now": ("አሁን ይግቡ", "Ammaa seeni"),
    "Log in": ("ግባ", "Seeni"),
    "Sign out": ("ውጣ", "Ba'i"),
    "Log out": ("ውጣ", "Ba'i"),
    "Forgot password?": ("የይለፍ ቃል ረስተዋል?", "Jecha icciitii irraanfadaa?"),
    "Forgot your password?": ("የይለፍ ቃል ረስተዋል?", "Jecha icciitii irraanfadaa?"),
    "Back to sign in": ("ወደ መግቢያ ተመልስ", "Deebi'ii seeni"),
    "Protected by brute-force lockout.": (
        "በመከላከያ እገዳ የተጠበቀ።", "Eegama icciitii."),
    "All sign-ins are monitored and audited.": (
        "ሁሉም መግቢያዎች ተከታተለው ይመዝገባሉ።", "Seeni hunduu ilaalamu galmeeffamu."),
    "Please enter a correct %(username)s and password. Note that both fields may be case-sensitive.": (
        "", "Maqaa fayyadamaa fi jecha icciitii sirrii galchi."),
    # --- Password reset flow ---
    "Reset your password": ("", ""),
    "Enter the email address linked to your admin account. We'll send you a one-time link to set a new password.": (
        "አዲስ የይለፍ ቃል ለማስቀመጥ አገናኝ እንልክልዎታለን። ኢሜይል አድራሻዎን ያስገቡ።",
        "Jecha icciitii haaraa murteesuuf hidhaa tokko ergina. Teessoo iimeelii kee galchi."),
    "Send reset link": ("አገናኙን ይላኩ", "Hidhaa ergi"),
    "Check your inbox": ("የገቢ መልዕክቶ ይፈትሹ", "Sanduuqa kee ilaali"),
    "If an account exists for that email, a one-time reset link is on its way. It expires shortly for security — check your spam folder too.": (
        "የዚህ ኢሜይል መግቢያ ካለዎት፣ አንድ ጊዜ የሚሠራ አገናኝ እየተላከ ነው። ለደህንነት ለአጭር ጊዜ ብቻ ይሠራል — የስፓም ማህደርዎንም ይፈትሹ።",
        "Iimeelii kanaan seenaa jiraate, hidhaa tokko ergameera. Yeroo gabaabaa waan dhumeef — sapphurruu kee ilaali."),
    "Set a new password": ("አዲስ የይለፍ ቃል ያስቀምጡ", "Jecha icciitii haaraa murteessi"),
    "Choose a strong password for the admin portal.": (
        "ለአስተዳደር ገጽ ጠንካራ የይለፍ ቃል ይምረጡ።", "Jecha icciitii cimaa murteessi."),
    "New password": ("አዲስ የይለፍ ቃል", "Jecha icciitii haaraa"),
    "Confirm new password": ("አዲሱን የይለፍ ቃል ያረጋግጡ", "Jecha icciitii haaraa mirkaneessi"),
    "Update password": ("የይለፍ ቃል ያዘምኑ", "Jecha icciitii jijjiiri"),
    "Link expired": ("", "Hidhaa dhumeera"),
    "This reset link is invalid or has already been used.": (
        "ይህ አገናኝ ትክክል አይደለም ወይም ቀድሞ ተጠቅመዋል።",
        "Hidhaan kun sirrii miti yookaan dursee fayyadamameera."),
    "Request a new link": ("አዲስ አገናኝ ይጠይቁ", "Hidhaa haaraa gaafadhu"),
    "Password updated": ("የይለፍ ቃል ተዘምኗል", "Jecha icciitii jijjiirameera"),
    "Your new password is active. You can now sign in with it.": (
        "አዲሱ የይለፍ ቃል ተግባራ ነው። በዚሁ ይግቡ።",
        "Jecha icciitii haaraa hojjee jira. Ammaa seenuu dandeessisi."),
    # --- Get Involved page / tab labels (exact text incl. emoji) ---
    "Pray, partner, give, or serve with us across the Horn of Africa.": (
        "ይጸልዩ፣ አጋር ይሁኑ፣ ስጡ ወይም ከእኛ ጋር ይሰሩ።",
        "Duaa kadhachaa, gargaarsaa, kennaa yookaan nu wajjin hojjechaa."),
    "Prayer": ("ጸሎት", "Duaa"),
    "Church Partnership": ("የሰበካ ቤት አጋርነት", "Waldaa Gargaarsa"),
    "Giving": ("ልገሳ", "Kennaa"),
    "Volunteer / Staff": ("በቃሌት / ሠራተኛ", "Hojjetaa/Miseensaa"),
    "Join the Prayer Network": ("የጸሎት ኔትዎርክ ተቀላቀሉ", "Walitti Dhufeenya Duaa hirmaadhaa"),
    "Receive weekly or monthly points for the peoples and hubs of the Horn.": (
        "ሳምንታዊ ወይም ወርሃዊ የጸሎት ቃል ይደርስልዎታል።",
        "Torbanii fi ji'a tokko tokko."),
    "Sign up to pray": ("ለጸሎት ተመዝገቡ", "Duaa raawwachuuf galmaa'i"),
    "Church Partnership Application": ("የሰበካ ቤት አጋር ጥያቄ", "Waldaa Gargaarsa"),
    "Giving Options": ("የልገሳ አማራጮች", "Karaa Kennaa"),
    "Volunteer / Staff Application": ("የበቃሌት / ሠራተኛ ጥያቄ", "Hojjetaa/Miseensaa"),
    "Submit application": ("ጥያቄውን ያስገቡ", "Gaaffii ergi"),
    "Close": ("ዝጋ", "Cufi"),
    "Oops": ("", ""),
    "Thank you!": ("እናመሰግናለን!", "Galatoomi!"),
    # --- Public form success messages (views.py) ---
    "Thank you — you've joined the prayer network!": (
        "እናመሰግናለን — የጸሎት ኔትዎርኩ ተቀላቀላችሁ!",
        "Galatoomi — Waldaa Duaa hirmaattani!"),
    "Application received — our partnerships team will be in touch.": (
        "ጥያቄው ደርሷል — የአጋርነት ቡድናችን ያገኛል።",
        "Gaaffii daaphetee — gargaarsi isin qunnama."),
    "Application received — thank you for offering to serve!": (
        "ጥያቄው ደርሷል — ለማገልገል በማሰባችሁ ናመሰግናለን!",
        "Gaaffii daaphetee — hojjettiif Galatoomi!"),
    "Access request submitted — we'll follow up by email.": (
        "ጥያቄው ግቦት ደርሷል — በኢሜይል እንከታተላለን።",
        "Gaaffii daaphetee — iimeelii ilaalna."),
    # --- Django admin chrome (applies to the admin portal) ---
    "Home": ("መነሻ", "Seensa"),
    "Add": ("ጨምር", "Dabali"),
    "Change": ("", "Baddali"),
    "Delete": ("", "Haaquu"),
    "Save": ("", "Olkaa'i"),
    "History": ("", "Seenaa"),
    "Dashboard": ("ዳሽቦርድ", "Sakatta'iinsa"),
    "View site": ("", "Saayitii ilaali"),
    
}


def build(code: str, index: int) -> None:
    po = polib.POFile()
    po.metadata = {
        "Project-Id-Version": "HO-ME 1.0",
        "Language": code,
        "Content-Type": "text/plain; charset=UTF-8",
        "Plural-Forms": "nplurals=2; plural=(n != 1);",
    }
    count = 0
    for msgid, (am, om) in TRANSLATIONS.items():
        po.append(polib.POEntry(msgid=msgid, msgstr=(am if code == "am" else om)))
        count += 1
    lc_dir = LOCALE_DIR / code / "LC_MESSAGES"
    lc_dir.mkdir(parents=True, exist_ok=True)
    po_path = lc_dir / "django.po"
    mo_path = lc_dir / "django.mo"
    po.save(str(po_path))
    po.save_as_mofile(str(mo_path))
    print(f"{code}: {count} msgids -> {po_path.name} + {mo_path.name} OK")


# Merge the whole-site sweep entries (kept in a separate module for size).
try:
    from .extra_translation_entries import EXTRA_TRANSLATIONS
    TRANSLATIONS.update(EXTRA_TRANSLATIONS)
except ImportError:  # run as a plain script, not as a package
    import sys as _sys, os as _os
    _sys.path.insert(0, str(LOCALE_DIR))
    from extra_translation_entries import EXTRA_TRANSLATIONS
    TRANSLATIONS.update(EXTRA_TRANSLATIONS)


if __name__ == "__main__":
    build("am", 1)
    build("om", 2)
    print("Done.")


