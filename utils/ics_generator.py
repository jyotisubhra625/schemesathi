"""
iCalendar (.ics) Generator for SchemeSaathi.
Generates standard calendar event files for government verification reminders.
"""

def generate_ics_reminder(scheme_name: str, app_id: str, reminder_date: str = "2026-08-01", citizen_name: str = "Citizen") -> bytes:
    """Generates standard RFC 5545 iCalendar (.ics) content bytes."""
    clean_date = reminder_date.replace("-", "").strip() if reminder_date else "20260801"
    if len(clean_date) > 8:
        clean_date = clean_date[:8]

    ics_str = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//SchemeSaathi//Government Scheme Followup//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
SUMMARY:SchemeSaathi Follow-up: {scheme_name}
DESCRIPTION:Namaste {citizen_name}! Follow-up reminder for your {scheme_name} application ({app_id}). Check portal or Gram Panchayat office.
DTSTART:{clean_date}T090000Z
DTEND:{clean_date}T100000Z
STATUS:CONFIRMED
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder: {scheme_name} Status Check
TRIGGER:-PT12H
END:VALARM
END:VEVENT
END:VCALENDAR"""
    return ics_str.encode("utf-8")

if __name__ == "__main__":
    res = generate_ics_reminder("PM-KISAN", "APP-2026-PMKI-12345")
    print(f"Generated ICS bytes length: {len(res)}")
