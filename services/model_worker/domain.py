"""Auditable domain support engines. ML readiness is separate from support completion."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import date, datetime
from difflib import unified_diff
from urllib.parse import urlsplit
import re, math, unicodedata


class InputError(ValueError):
    pass


BN = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def normalize(v):
    return unicodedata.normalize("NFC", str(v)).translate(BN)


def number(v, minimum=0, maximum="1000000000000"):
    try:
        d = Decimal(normalize(v).replace(",", "").strip())
        if not d.is_finite() or d < Decimal(str(minimum)) or d > Decimal(str(maximum)):
            raise InputError(
                "Number outside permitted range / সংখ্যাটি অনুমোদিত সীমার বাইরে"
            )
        return d
    except (InvalidOperation, TypeError):
        raise InputError("Enter a valid number / সঠিক সংখ্যা লিখুন")


def amount(v):
    return str(number(v).quantize(Decimal(".01"), rounding=ROUND_HALF_UP))


def text(p, key="text", required=True):
    v = p.get(key, "")
    if not isinstance(v, str) or len(v) > 20000:
        raise InputError(
            "Text must contain at most 20,000 characters / সর্বোচ্চ ২০,০০০ অক্ষর"
        )
    v = v.strip()
    if required and not v:
        raise InputError("Text is required / লেখা আবশ্যক")
    return v


def rows(p, required=True):
    a = p.get("rows", [])
    if not isinstance(a, list) or len(a) > 200:
        raise InputError("Supply at most 200 records / সর্বোচ্চ ২০০টি রেকর্ড")
    if required and not a:
        raise InputError("Add a record / একটি রেকর্ড যোগ করুন")
    if not all(isinstance(x, dict) for x in a):
        raise InputError("Invalid records / ভুল রেকর্ড")
    return a


def n(p, key, default=None, **kw):
    if key not in p and default is None:
        raise InputError(f"Missing field / ঘরটি পূরণ করুন: {key}")
    return number(p.get(key, default), **kw)


def field(key, bn, en, kind="text", **kw):
    return {"key": key, "bn": bn, "en": en, "type": kind, **kw}


def table(*cols):
    return field(
        "rows",
        "রেকর্ডসমূহ",
        "Records",
        "table",
        columns=[{"key": a, "bn": b, "en": c, "type": d} for a, b, c, d in cols],
    )


NAME = ("name", "নাম", "Name", "text")
VALUE = ("value", "মান", "Value", "number")
DATE = ("date", "তারিখ", "Date", "date")
UNIT = ("unit", "একক", "Unit", "text")
NOTE = field(
    "text", "নিজের পর্যবেক্ষণ বা লেখা", "Your observations or text", "textarea"
)
F = {
    "observation": [
        field("ph", "pH (ঐচ্ছিক)", "pH (optional)", "number", optional=True),
        field(
            "oxygen",
            "মাপা DO mg/L (ঐচ্ছিক)",
            "Measured DO mg/L (optional)",
            "number",
            optional=True,
        ),
        NOTE,
    ],
    "image_compare": [NOTE],
    "crop_diary": [
        field("area", "নিজে মাপা জমির আয়তন", "Manually measured area", "number"),
        field(
            "affected",
            "নিজের অনুমিত ক্ষতিগ্রস্ত আয়তন",
            "Self-reported affected area",
            "number",
        ),
        field("unit", "উভয় মাপের একই একক", "Same explicit unit"),
        NOTE,
    ],
    "roof": [
        field("area", "ছাদের মাপ (বর্গমিটার)", "Roof area (m²)", "number"),
        field("rate", "প্রতি বর্গমিটারের খরচ (৳)", "Cost per m² (BDT)", "number"),
        field(
            "rain", "দৃশ্যপটে বৃষ্টির পরিমাণ (mm)", "Scenario rainfall (mm)", "number"
        ),
        field(
            "coefficient",
            "নিজে নির্ধারিত সংগ্রহ অনুপাত ০–১",
            "Assumed runoff coefficient 0–1",
            "number",
        ),
    ],
    "audio": [NOTE],
    "contract": [
        NOTE,
        field(
            "comparison",
            "দ্বিতীয় খসড়া (ঐচ্ছিক)",
            "Second draft (optional)",
            "textarea",
            optional=True,
        ),
    ],
    "bill": [
        table(NAME, ("amount", "চার্জ (৳)", "Charge (BDT)", "number")),
        field("declared", "বিলে লেখা মোট (৳)", "Stated total (BDT)", "number"),
    ],
    "care": [NOTE],
    "video": [NOTE],
    "inventory": [
        table(
            NAME,
            ("quantity", "নিশ্চিত স্টক", "Confirmed quantity", "number"),
            ("minimum", "রিঅর্ডার সীমা", "Reorder threshold", "number"),
            ("expiry", "মেয়াদ (ঐচ্ছিক)", "Expiry (optional)", "date"),
        )
    ],
    "prices": [
        table(
            NAME,
            ("market", "বাজার", "Market", "text"),
            ("price", "মূল্য (৳)", "Price (BDT)", "number"),
            ("quantity", "পরিমাণ", "Quantity", "number"),
            UNIT,
            DATE,
        )
    ],
    "home": [NOTE],
    "waste": [NOTE],
    "worksite": [NOTE],
    "directory": [field("text", "জেলা বা সেবার নাম", "District or service")],
    "lab": [field("unit", "একই ল্যাব একক", "Same laboratory unit"), table(DATE, VALUE)],
    "prescription": [NOTE],
    "vaccine": [table(NAME, DATE)],
    "maternal": [NOTE],
    "counts": [table(DATE, VALUE)],
    "rent": [
        field("rent", "মাসিক ভাড়া (৳)", "Monthly rent (BDT)", "number"),
        field("service", "সার্ভিস চার্জ (৳)", "Service charge (BDT)", "number"),
        field("utilities", "অনুমিত ইউটিলিটি (৳)", "Assumed utilities (BDT)", "number"),
        field("deposit", "ফেরতযোগ্য জামানত (৳)", "Refundable deposit (BDT)", "number"),
    ],
    "road": [
        field(
            "location",
            "আনুমানিক এলাকা; ব্যক্তিগত ঠিকানা নয়",
            "Approximate area; no private address",
        ),
        NOTE,
    ],
    "route": [
        field("origin", "শুরু", "Origin"),
        field("destination", "গন্তব্য", "Destination"),
        table(
            ("from", "শুরু", "From", "text"),
            ("to", "শেষ", "To", "text"),
            ("cost", "নিজের দেওয়া ব্যয়", "Entered edge cost", "number"),
        ),
    ],
    "water": [
        table(
            NAME,
            VALUE,
            UNIT,
            ("lower", "ল্যাবের নিম্নসীমা", "Lab lower bound", "number"),
            ("upper", "ল্যাবের ঊর্ধ্বসীমা", "Lab upper bound", "number"),
        )
    ],
    "farm": [
        field("cost", "মোট খরচ (৳)", "Total cost (BDT)", "number"),
        field("yield", "সম্ভাব্য বিক্রয় পরিমাণ", "Assumed sale quantity", "number"),
        field("price", "ধরা একক মূল্য (৳)", "Assumed unit price (BDT)", "number"),
    ],
    "livestock": [
        field("unit", "ওজনের একই একক", "Same weight unit"),
        table(DATE, VALUE),
    ],
    "form": [
        field(
            "required",
            "আপনার তালিকার প্রয়োজনীয় কাগজ (প্রতি লাইনে একটি)",
            "Your required documents (one per line)",
            "textarea",
        ),
        field(
            "available",
            "আপনার কাছে আছে (প্রতি লাইনে একটি)",
            "Documents you have (one per line)",
            "textarea",
        ),
    ],
    "heat": [
        field("temperature", "মাপা তাপমাত্রা °C", "Measured temperature °C", "number"),
        field("humidity", "আপেক্ষিক আর্দ্রতা %", "Relative humidity %", "number"),
    ],
    "hospital_bill": [],
    "blood": [
        field(
            "group",
            "রক্তের গ্রুপ",
            "Blood group",
            "select",
            options=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
        ),
        field("district", "জেলা", "District"),
        field("date", "অনুরোধের মেয়াদ", "Request expiry", "date"),
    ],
    "rag": [
        field("text", "আপনার প্রশ্ন", "Your question"),
        field("grade", "শ্রেণি (ঐচ্ছিক)", "Grade (optional)", optional=True),
    ],
    "reading": [
        field(
            "passage_id",
            "পাঠ",
            "Passage",
            "select",
            options=["AUTH-READ-01", "AUTH-READ-02"],
        ),
        field(
            "text",
            "পাঠটি দেখে নিজে টাইপ করুন",
            "Type your reading practice",
            "textarea",
        ),
    ],
    "land": [
        field("value", "পরিমাণ", "Area value", "number"),
        field(
            "unit",
            "স্পষ্ট একক",
            "Explicit unit",
            "select",
            options=["acre", "decimal", "shotok", "square_foot"],
        ),
        field(
            "comparison",
            "দ্বিতীয় নথির পরিমাণ, একই একক (ঐচ্ছিক)",
            "Second document value, same unit (optional)",
            "number",
            optional=True,
        ),
    ],
    "wage": [
        field("hours", "সাধারণ ঘণ্টা", "Regular hours", "number"),
        field(
            "rate",
            "নিজের চুক্তির ঘণ্টাপ্রতি হার (৳)",
            "Your contractual hourly rate (BDT)",
            "number",
        ),
        field("overtime", "অতিরিক্ত ঘণ্টা", "Overtime hours", "number"),
        field(
            "multiplier",
            "চুক্তিতে সম্মত গুণক",
            "Contractual overtime multiplier",
            "number",
        ),
        field("paid", "পেয়েছেন (৳)", "Amount paid (BDT)", "number"),
    ],
    "phraseboard": [
        field("text", "বড় করে দেখানোর লেখা", "Text to display", "textarea")
    ],
    "drain": [
        field("location", "আনুমানিক এলাকা বা ওয়ার্ড", "Approximate area or ward"),
        NOTE,
    ],
    "fire": [
        field("exits", "নিজের গণনা করা বের হওয়ার পথ", "Entered exit count", "number"),
        field("blocked", "বন্ধ পথ", "Blocked exits", "number"),
        NOTE,
    ],
    "soil": [],
    "energy": [
        table(
            NAME,
            ("watts", "ওয়াট", "Watts", "number"),
            ("hours", "দৈনিক ঘণ্টা", "Daily hours", "number"),
            ("count", "সংখ্যা", "Count", "number"),
        ),
        field("days", "দিন", "Days", "number"),
        field(
            "rate",
            "নিজে নিশ্চিত করা একক হার (৳/kWh)",
            "Your confirmed rate (BDT/kWh)",
            "number",
        ),
    ],
    "scam": [
        NOTE,
        field(
            "url", "সন্দেহজনক URL (ঐচ্ছিক)", "Suspicious URL (optional)", optional=True
        ),
    ],
    "pharmacy": [field("text", "ওষুধের বানান ও শহর", "Medicine spelling and city")],
    "service": [],
    "travel": [],
    "skills": [
        field(
            "skills",
            "আপনার দক্ষতা, প্রতি লাইনে একটি",
            "Your skills, one per line",
            "textarea",
        ),
        field(
            "required",
            "আপনার নির্বাচিত কাজের প্রয়োজন, প্রতি লাইনে একটি",
            "Requirements from your chosen job, one per line",
            "textarea",
        ),
    ],
    "food": [
        NOTE,
        field(
            "allergens",
            "যে নাম খুঁজবেন, প্রতি লাইনে একটি",
            "Names to look for, one per line",
            "textarea",
        ),
    ],
    "benefits": [],
    "repair": [
        field("repair", "মেরামতের কোট (৳)", "Repair quote (BDT)", "number"),
        field("replace", "নতুন পণ্যের দাম (৳)", "Replacement cost (BDT)", "number"),
        NOTE,
    ],
    "bulletin": [
        NOTE,
        field(
            "issued_at",
            "প্রকাশনার সময়, উৎসে যেমন আছে",
            "Issued time as printed by source",
        ),
        field("source_url", "আপনার দেওয়া উৎসের URL", "Your source URL"),
    ],
    "school": [NOTE],
    "cashbook": [
        field("opening", "শুরুর নগদ (৳)", "Opening cash (BDT)", "number"),
        table(
            NAME,
            ("incoming", "আয় (৳)", "Cash in (BDT)", "number"),
            ("outgoing", "ব্যয় (৳)", "Cash out (BDT)", "number"),
        ),
        field(
            "counted", "হাতে গোনা শেষ নগদ (৳)", "Counted closing cash (BDT)", "number"
        ),
    ],
}
for a, b in [
    ("hospital_bill", "bill"),
    ("soil", "water"),
    ("service", "form"),
    ("travel", "route"),
    ("benefits", "form"),
]:
    F[a] = F[b]


def result(method, facts, detail=None, warnings=None):
    return {
        "status": "support_completed",
        "method": method,
        "model_version": "mouchak-rules-1.0",
        "facts": facts,
        "details": detail or {},
        "uncertainties": warnings or [],
        "references": [
            {
                "title": "User-confirmed input / ব্যবহারকারীর নিশ্চিত তথ্য",
                "kind": "user_provided",
                "official": False,
            }
        ],
        "full_module_complete": False,
    }


def process(engine, p, context=None):
    context = context or {}
    if engine == "video" and context.get("pose"):
        return context["pose"]
    if engine in ["directory", "pharmacy", "video"]:
        raise InputError(
            "Unavailable: approved records or evaluated specialized model are not installed / অনুমোদিত তথ্য বা পরীক্ষিত বিশেষায়িত মডেল নেই"
        )
    if engine in ["bill", "hospital_bill"]:
        a = rows(p)
        vals = [n(x, "amount") for x in a]
        total = sum(vals, Decimal(0))
        declared = n(p, "declared")
        seen = set()
        dups = []
        for x in a:
            k = (normalize(x.get("name", "")).casefold(), str(n(x, "amount")))
            if k in seen:
                dups.append(x.get("name"))
            seen.add(k)
        return result(
            "Exact decimal reconciliation / দশমিক যোগফল",
            {
                "line_total_bdt": amount(total),
                "stated_total_bdt": amount(declared),
                "difference_bdt": str((declared - total).quantize(Decimal(".01"))),
                "exact_repeated_items": dups,
            },
            a,
            [
                "Repeated items may be intentional; ask the issuer. / একই চার্জ একাধিকবার থাকা বৈধও হতে পারে।"
            ],
        )
    if engine == "energy":
        a = rows(p)
        days = n(p, "days", maximum=366)
        rate = n(p, "rate")
        details = []
        for x in a:
            kwh = (
                n(x, "watts", maximum=1000000)
                * n(x, "hours", maximum=24)
                * n(x, "count", maximum=10000)
                * days
                / 1000
            )
            details.append(
                {"name": x.get("name"), "kwh": str(kwh), "cost_bdt": amount(kwh * rate)}
            )
        kwh = sum((Decimal(x["kwh"]) for x in details), Decimal(0))
        return result(
            "W × hours × count × days ÷ 1000",
            {"total_kwh": str(kwh), "energy_only_cost_bdt": amount(kwh * rate)},
            details,
            [
                "Your rate is a scenario, not a verified official tariff. Taxes and fixed fees excluded. / কর ও স্থায়ী চার্জ অন্তর্ভুক্ত নয়।"
            ],
        )
    if engine == "land":
        v = n(p, "value")
        unit = p.get("unit")
        factors = {
            "acre": Decimal(100),
            "decimal": Decimal(1),
            "shotok": Decimal(1),
            "square_foot": Decimal(1) / Decimal("435.6"),
        }
        if unit not in factors:
            raise InputError(
                "Explicit supported unit required; bigha is regional / স্পষ্ট একক দিন; বিঘার আঞ্চলিক মাপ প্রযোজ্য"
            )
        d = v * factors[unit]
        facts = {
            "original_value": str(v),
            "original_unit": unit,
            "decimal": str(d),
            "acre": str(d / 100),
            "square_foot": str(d * Decimal("435.6")),
        }
        if p.get("comparison") not in [None, ""]:
            facts["document_difference_same_unit"] = str(v - n(p, "comparison"))
        return result(
            "Exact unit conversion / একক রূপান্তর",
            facts,
            warnings=[
                "No title, ownership or legal validity determination. / মালিকানা বা দলিলের বৈধতা যাচাই নয়।"
            ],
        )
    if engine == "wage":
        base = n(p, "hours") * n(p, "rate")
        ot = n(p, "overtime") * n(p, "rate") * n(p, "multiplier", maximum=10)
        paid = n(p, "paid")
        return result(
            "User-defined contractual scenario / নিজের চুক্তির হিসাব",
            {
                "base_bdt": amount(base),
                "overtime_bdt": amount(ot),
                "scenario_total_bdt": amount(base + ot),
                "paid_bdt": amount(paid),
                "difference_bdt": str((base + ot - paid).quantize(Decimal(".01"))),
            },
            warnings=[
                "Not a legal entitlement calculation; applicable law is not verified. / আইনি পাওনার ঘোষণা নয়।"
            ],
        )
    if engine == "farm":
        c = n(p, "cost")
        y = n(p, "yield", minimum=".000001")
        price = n(p, "price")
        revenue = y * price
        return result(
            "Break-even scenario / লাভ-ক্ষতির দৃশ্যপট",
            {
                "cost_bdt": amount(c),
                "scenario_revenue_bdt": amount(revenue),
                "scenario_profit_bdt": str((revenue - c).quantize(Decimal(".01"))),
                "break_even_unit_price_bdt": amount(c / y),
            },
            warnings=[
                "User assumptions only; no future price forecast. / ভবিষ্যৎ দামের পূর্বাভাস নয়।"
            ],
        )
    if engine == "cashbook":
        a = rows(p)
        inc = sum((n(x, "incoming") for x in a), Decimal(0))
        out = sum((n(x, "outgoing") for x in a), Decimal(0))
        closing = n(p, "opening") + inc - out
        return result(
            "Cash reconciliation / নগদ মিল",
            {
                "cash_in_bdt": amount(inc),
                "cash_out_bdt": amount(out),
                "calculated_closing_bdt": str(closing.quantize(Decimal(".01"))),
                "counted_closing_bdt": amount(n(p, "counted")),
                "difference_bdt": str(
                    (n(p, "counted") - closing).quantize(Decimal(".01"))
                ),
            },
            a,
            [
                "Cash movement is not profit unless all costs are known. / নগদ প্রবাহ মানেই লাভ নয়।"
            ],
        )
    if engine == "prices":
        a = rows(p)
        details = []
        factors = {
            "kg": ("kg", Decimal(1)),
            "g": ("kg", Decimal(".001")),
            "l": ("l", Decimal(1)),
            "ml": ("l", Decimal(".001")),
            "piece": ("piece", Decimal(1)),
        }
        for x in a:
            u = normalize(x.get("unit", "")).lower()
            q = n(x, "quantity", minimum=".000001")
            price = n(x, "price")
            if u not in factors:
                raise InputError(
                    "Use kg, g, l, ml or piece / kg, g, l, ml অথবা piece দিন"
                )
            day = date.fromisoformat(text(x, "date"))
            if day > date.today():
                raise InputError(
                    "A recorded price cannot have a future date / ভবিষ্যৎ তারিখে দেখা দাম নয়"
                )
            base, m = factors[u]
            details.append(
                {
                    "name": text(x, "name"),
                    "market": text(x, "market"),
                    "date": str(day),
                    "unit": base,
                    "unit_price_bdt": amount(price / (q * m)),
                    "source": "user-entered; not official",
                }
            )
        return result(
            "Comparable unit-price normalization / একক দরের তুলনা",
            {"offers": len(details)},
            sorted(
                details,
                key=lambda x: (x["name"], x["unit"], Decimal(x["unit_price_bdt"])),
            ),
            [
                "Compare only the same product, quality and unit. No current official prices were loaded. / একই পণ্য ও মান তুলনা করুন।"
            ],
        )
    if engine == "inventory":
        a = rows(p)
        details = []
        for x in a:
            q = n(x, "quantity")
            low = q <= n(x, "minimum")
            exp = x.get("expiry")
            expired = bool(exp and date.fromisoformat(exp) < date.today())
            details.append(
                {
                    "name": text(x, "name"),
                    "confirmed_quantity": str(q),
                    "reorder": low,
                    "expiry": exp or None,
                    "expired": expired,
                }
            )
        return result(
            "Confirmed inventory thresholds / নিশ্চিত স্টকের সীমা",
            {"items": len(a), "reorder_count": sum(x["reorder"] for x in details)},
            details,
        )
    if engine in ["lab", "livestock", "counts"]:
        a = rows(p)
        out = []
        for x in a:
            out.append(
                {
                    "date": str(date.fromisoformat(text(x, "date"))),
                    "value": str(n(x, "value")),
                }
            )
        if len({x["date"] for x in out}) != len(out):
            raise InputError("Use one value per date / প্রতি তারিখে একটি মান দিন")
        out.sort(key=lambda x: x["date"])
        delta = Decimal(out[-1]["value"]) - Decimal(out[0]["value"])
        unit = "count" if engine == "counts" else text(p, "unit")
        return result(
            "Descriptive time series, no forecast / পর্যবেক্ষণের ধারাবাহিকতা",
            {
                "observations": len(out),
                "unit": unit,
                "change_first_to_last": str(delta),
            },
            out,
            [
                "No diagnosis, outbreak forecast or clinical range is inferred. / রোগ নির্ণয় বা পূর্বাভাস নয়।"
            ],
        )
    if engine in ["water", "soil"]:
        a = rows(p)
        out = []
        for x in a:
            v = n(x, "value")
            lo = n(x, "lower")
            hi = n(x, "upper")
            if lo > hi:
                raise InputError(
                    "Lower reference bound exceeds upper bound / নিম্নসীমা ঊর্ধ্বসীমার চেয়ে বেশি"
                )
            out.append(
                {
                    "name": text(x, "name"),
                    "value": str(v),
                    "unit": text(x, "unit"),
                    "provided_lower": str(lo),
                    "provided_upper": str(hi),
                    "comparison": (
                        "below"
                        if v < lo
                        else "above" if v > hi else "within provided interval"
                    ),
                }
            )
        return result(
            "Comparison to user-supplied lab intervals / নিজের ল্যাবের সীমার সাথে তুলনা",
            {"measurements": len(out)},
            out,
            [
                "No official safety limit, potability certificate or fertilizer dose is supplied. / নিরাপদ পানি বা সারের মাত্রার ঘোষণা নয়।"
            ],
        )
    if engine in ["form", "service", "benefits", "skills"]:
        required = [s.strip() for s in text(p, "required").splitlines() if s.strip()]
        key = "skills" if engine == "skills" else "available"
        provided = {
            s.strip().casefold() for s in text(p, key, False).splitlines() if s.strip()
        }
        matched = [s for s in required if s.casefold() in provided]
        missing = [s for s in required if s.casefold() not in provided]
        return result(
            "Explicit checklist comparison / নিজের তালিকার তুলনা",
            {
                "listed_requirements": len(required),
                "matched": matched,
                "remaining": missing,
            },
            warnings=[
                "Your checklist is not an official service, admission or eligibility determination. / এটি সরকারি যোগ্যতা বা সেবাপ্রাপ্তির সিদ্ধান্ত নয়।"
            ],
        )
    if engine in ["route", "travel"]:
        import networkx as nx

        g = nx.DiGraph()
        a = rows(p)
        for x in a:
            g.add_edge(text(x, "from"), text(x, "to"), weight=float(n(x, "cost")))
        start = text(p, "origin")
        end = text(p, "destination")
        try:
            path = nx.shortest_path(g, start, end, weight="weight")
            cost = nx.path_weight(g, path, "weight")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            raise InputError(
                "No path in the supplied network / নিজের দেওয়া নেটওয়ার্কে পথ নেই"
            )
        return result(
            "NetworkX Dijkstra on user-provided directed edges",
            {"path": path, "total_entered_cost": str(cost)},
            warnings=[
                "No live traffic, safety guarantee or official route data. / সরাসরি ট্রাফিক বা নিরাপত্তার নিশ্চয়তা নয়।"
            ],
        )
    if engine == "heat":
        c = float(n(p, "temperature", minimum=-50, maximum=65))
        rh = float(n(p, "humidity", maximum=100))
        f = c * 9 / 5 + 32
        simple = 0.5 * (f + 61 + (f - 68) * 1.2 + rh * 0.094)
        hi = (simple + f) / 2
        if hi >= 80:
            hi = (
                -42.379
                + 2.04901523 * f
                + 10.14333127 * rh
                - 0.22475541 * f * rh
                - 0.00683783 * f * f
                - 0.05481717 * rh * rh
                + 0.00122874 * f * f * rh
                + 0.00085282 * f * rh * rh
                - 0.00000199 * f * f * rh * rh
            )
            if rh < 13 and 80 <= f <= 112:
                hi -= ((13 - rh) / 4) * math.sqrt((17 - abs(f - 95)) / 17)
            elif rh > 85 and 80 <= f <= 87:
                hi += ((rh - 85) / 10) * ((87 - f) / 5)
        value = (hi - 32) * 5 / 9
        return result(
            "NOAA Rothfusz heat-index approximation, shaded conditions",
            {
                "temperature_c": c,
                "humidity_percent": rh,
                "estimated_heat_index_c": round(value, 1),
            },
            warnings=[
                "Not an official alert or work-rest prescription; direct sun and exertion change risk. / সরকারি সতর্কতা বা কাজের সময়ের নির্দেশ নয়।"
            ],
        )
    if engine == "rent":
        monthly = n(p, "rent") + n(p, "service") + n(p, "utilities")
        deposit = n(p, "deposit")
        return result(
            "Household cost scenario / মাসিক খরচ",
            {
                "monthly_bdt": amount(monthly),
                "annual_recurring_bdt": amount(monthly * 12),
                "refundable_deposit_bdt": amount(deposit),
                "first_month_cash_bdt": amount(monthly + deposit),
            },
            warnings=[
                "No market fairness or legal conclusion. / ন্যায্য ভাড়া বা আইনি সিদ্ধান্ত নয়।"
            ],
        )
    if engine == "roof":
        area = n(p, "area")
        rain = n(p, "rain")
        coef = n(p, "coefficient", maximum=1)
        rate = n(p, "rate")
        return result(
            "Roof area × cost; m² × rainfall mm × runoff fraction",
            {
                "scenario_cost_bdt": amount(area * rate),
                "scenario_collected_litres": str(area * rain * coef),
            },
            warnings=[
                "Not structural certification or measured cooling prediction. / প্রকৌশল সনদ বা শীতলতার পূর্বাভাস নয়।"
            ],
        )
    if engine == "crop_diary":
        area = n(p, "area", minimum=".000001")
        affected = n(p, "affected")
        if affected > area:
            raise InputError(
                "Affected area exceeds total / ক্ষতিগ্রস্ত আয়তন মোটের বেশি"
            )
        return result(
            "Self-reported area calculation / নিজের দেওয়া আয়তনের হিসাব",
            {
                "total": str(area),
                "self_reported_affected": str(affected),
                "unit": text(p, "unit"),
                "self_reported_fraction_percent": str(affected / area * 100),
                "note": text(p),
            },
            warnings=[
                "No damage inferred from photographs; no compensation estimate. / ছবি থেকে ক্ষতি বা ক্ষতিপূরণ অনুমান নয়।"
            ],
        )
    if engine == "fire":
        exits = n(p, "exits", maximum=1000)
        blocked = n(p, "blocked", maximum=1000)
        if blocked > exits or exits % 1 or blocked % 1:
            raise InputError("Invalid exit counts / পথের সংখ্যা সঠিক নয়")
        return result(
            "Entered constraint check / নিজের দেওয়া বাধার হিসাব",
            {
                "entered_exits": str(exits),
                "unblocked_entered_exits": str(exits - blocked),
                "notes": text(p),
            },
            warnings=[
                "This is not an inspection or evacuation safety certification. / পরিদর্শন বা নিরাপত্তা সনদ নয়।"
            ],
        )
    if engine == "repair":
        repair = n(p, "repair")
        replace = n(p, "replace", minimum=".01")
        return result(
            "Quote comparison / কোটের তুলনা",
            {
                "repair_bdt": amount(repair),
                "replacement_bdt": amount(replace),
                "repair_to_replace_percent": str(
                    (repair / replace * 100).quantize(Decimal(".1"))
                ),
                "notes": text(p),
            },
            warnings=[
                "No invasive electrical or gas repair instructions. / বৈদ্যুতিক বা গ্যাস যন্ত্র খুলে কাজের পরামর্শ নয়।"
            ],
        )
    if engine == "scam":
        s = text(p)
        url = text(p, "url", False)
        indicators = []
        patterns = [
            ("otp|ওটিপি|one.time.password", "Requests an OTP / ওটিপির অনুরোধ"),
            ("urgent|এখনই|জরুরি", "Pressure to act / তাড়াহুড়োর চাপ"),
            (
                "prize|lottery|পুরস্কার|লটারি",
                "Prize or lottery language / পুরস্কারের ভাষা",
            ),
            ("password|পাসওয়ার্ড", "Password request / পাসওয়ার্ডের অনুরোধ"),
        ]
        for pat, label in patterns:
            if re.search(pat, s, re.I):
                indicators.append(label)
        if url:
            u = urlsplit(url)
            if u.scheme not in ["http", "https"] or not u.hostname:
                raise InputError(
                    "Only a well-formed http(s) URL is accepted / সঠিক http(s) URL দিন"
                )
            if u.username or u.password:
                indicators.append(
                    "URL includes credentials or misleading @ / URL-এ পরিচয়তথ্য বা @ আছে"
                )
            if u.scheme != "https":
                indicators.append("No HTTPS / HTTPS নেই")
            if "xn--" in u.hostname:
                indicators.append(
                    "Internationalized domain; check spelling / ডোমেইনের বানান পরীক্ষা করুন"
                )
            host = u.hostname
        else:
            host = None
        safe = re.sub(r"\b[0-9০-৯]{4,}\b", "[REDACTED]", s)
        return result(
            "Transparent text and URL heuristics, not a trained fraud classifier",
            {
                "indicators": indicators,
                "domain_only": host,
                "redacted_text": safe,
                "link_opened": False,
            },
            warnings=[
                "Indicators cannot prove fraud or safety. Verify using a known independent channel. / নিশ্চিত প্রতারণা বা নিরাপত্তার সিদ্ধান্ত নয়।"
            ],
        )
    if engine == "food":
        s = text(p)
        terms = [x.strip() for x in text(p, "allergens").splitlines() if x.strip()]
        found = [x for x in terms if x.casefold() in s.casefold()]
        return result(
            "Explicit label term matching / লেবেলে লেখা শব্দের মিল",
            {
                "explicit_matches": found,
                "not_found_in_transcription": [x for x in terms if x not in found],
                "confirmed_transcription": s,
            },
            warnings=[
                "Absence from this transcription does not mean allergen-free; verify with manufacturer. / এখানে না থাকলেই অ্যালার্জেন নেই এমন নয়।"
            ],
        )
    if engine == "contract":
        s = text(p)
        other = text(p, "comparison", False)
        clauses = [x.strip() for x in re.split(r"[\n।;]+", s) if x.strip()]
        diff = (
            list(
                unified_diff(
                    s.splitlines(),
                    other.splitlines(),
                    fromfile="your-draft-1",
                    tofile="your-draft-2",
                    lineterm="",
                )
            )
            if other
            else []
        )
        return result(
            "Source-preserving clause split and text diff / শর্ত ভাগ ও খসড়ার পার্থক্য",
            {"clause_count": len(clauses)},
            {"clauses": clauses, "diff": diff},
            [
                "No legal RAG corpus is approved; no legal risk verdict is generated. / অনুমোদিত আইনি করপাস নেই; আইনি রায় নয়।"
            ],
        )
    if engine == "vaccine":
        a = rows(p)
        out = [
            {
                "name": text(x, "name"),
                "recorded_date": str(date.fromisoformat(text(x, "date"))),
            }
            for x in a
        ]
        return result(
            "User-recorded timeline / নিজের দেওয়া রেকর্ড",
            {"recorded_events": len(out)},
            sorted(out, key=lambda x: x["recorded_date"]),
            [
                "No official schedule or catch-up dose is inferred. Ask a clinician. / নতুন টিকার তারিখ অনুমান নয়।"
            ],
        )
    if engine == "blood":
        group = p.get("group")
        expiry = date.fromisoformat(text(p, "date"))
        if (
            group not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            or expiry < date.today()
        ):
            raise InputError(
                "Valid group and current expiry required / সঠিক গ্রুপ ও বর্তমান মেয়াদ দিন"
            )
        return result(
            "Private request preparation / ব্যক্তিগত অনুরোধ",
            {
                "blood_group_label": group,
                "district": text(p, "district"),
                "expiry": str(expiry),
                "donor_matches": [],
            },
            warnings=[
                "No donor directory is approved. No compatibility or fitness determination. / অনুমোদিত দাতা তালিকা নেই; চিকিৎসাগত সিদ্ধান্ত নয়।"
            ],
        )
    if engine == "waste":
        s = text(p).casefold()
        guide = {
            "plastic": (
                "প্লাস্টিক",
                "Keep clean and separate; check your local collector.",
            ),
            "কাগজ": ("কাগজ", "Keep dry and separate from food waste."),
            "battery": (
                "ব্যাটারি",
                "Keep separate; ask an authorized hazardous-waste collector.",
            ),
            "ব্যাটারি": (
                "ব্যাটারি",
                "আলাদা রাখুন; অনুমোদিত সংগ্রাহকের সঙ্গে কথা বলুন।",
            ),
            "glass": (
                "কাচ",
                "Protect others from sharp edges; check local collection.",
            ),
        }
        hits = [
            {"term": k, "material": v[0], "original_authored_note": v[1]}
            for k, v in guide.items()
            if k in s
        ]
        return result(
            "Project-authored material glossary; exact text match",
            {"matches": hits},
            warnings=[
                "No photo classification or verified recycling directory. / ছবি শনাক্তকরণ বা যাচাইকৃত সংগ্রাহকের তালিকা নয়।"
            ],
        )
    if engine == "observation":
        facts = {"observation": text(p)}
        if p.get("ph") not in [None, ""]:
            facts["measured_ph"] = str(n(p, "ph", maximum=14))
        if p.get("oxygen") not in [None, ""]:
            facts["measured_do_mg_l"] = str(n(p, "oxygen", maximum=100))
        return result(
            "Measured observation journal / মাপা পর্যবেক্ষণ",
            facts,
            warnings=[
                "No oxygen or fish disease inferred from images; no anomaly model fitted. / ছবি থেকে অক্সিজেন বা রোগ অনুমান নয়।"
            ],
        )
    if engine in ["image_compare", "drain"]:
        if context.get("image_comparison"):
            return result(
                "OpenCV feature registration and pixel difference",
                context["image_comparison"],
                warnings=[
                    "Lighting, viewpoint and seasons can create differences; not erosion or water segmentation. / আলো ও কোণের কারণে পার্থক্য হতে পারে।"
                ],
            )
        return result(
            "Dated observation preparation / তারিখসহ পর্যবেক্ষণ",
            {"notes": text(p), "location": text(p, "location", False)},
            warnings=[
                "Two images are needed for registration; no visual classification was performed. / ছবি তুলনা করা হয়নি।"
            ],
        )
    if engine == "audio":
        if context.get("noise_events"):
            return context["noise_events"]
        if context.get("audio"):
            return result(
                "Measured PCM signal statistics; not sound classification",
                context["audio"],
                warnings=[
                    "Uncalibrated signal levels are not environmental dB. / ক্যালিব্রেশন ছাড়া পরিবেশের dB নয়।"
                ],
            )
        raise InputError(
            "Upload a PCM WAV recording for signal inspection / PCM WAV দিন"
        )
    if engine == "rag":
        if not context.get("rag"):
            raise InputError("Embedding checkpoint unavailable / এমবেডিং মডেল নেই")
        return context["rag"]
    if engine == "reading":
        docs = context.get("documents", [])
        doc = next((x for x in docs if x["id"] == p.get("passage_id")), None)
        if not doc:
            raise InputError("Choose a passage / পাঠ নির্বাচন করুন")
        actual = text(p)
        expected = doc["text_bn"]
        expected_tokens = expected.split()
        actual_tokens = actual.split()
        import difflib

        matching = sum(
            x.size
            for x in difflib.SequenceMatcher(
                a=expected_tokens, b=actual_tokens, autojunk=False
            ).get_matching_blocks()
        )
        return result(
            "Typed word alignment, not pronunciation scoring",
            {
                "matched_words": matching,
                "expected_words": len(expected_tokens),
                "typed_words": len(actual_tokens),
                "passage_id": doc["id"],
            },
            {"original_passage": expected, "practice_text": actual},
            [
                "Typed practice does not measure speech or reading ability. / টাইপ করা অনুশীলন উচ্চারণের মূল্যায়ন নয়।"
            ],
        )
    if engine == "bulletin":
        url = text(p, "source_url")
        u = urlsplit(url)
        if u.scheme not in ["https", "http"] or not u.hostname:
            raise InputError("Valid source URL required / সঠিক উৎসের URL দিন")
        return result(
            "Preserved user-supplied bulletin / নিজের দেওয়া বুলেটিন",
            {
                "verbatim_text": text(p),
                "source_url": url,
                "issued_at_as_entered": text(p, "issued_at"),
                "official_status_verified": False,
            },
            warnings=[
                "No live BMD feed or source verification is connected. / সরাসরি সরকারি ফিড বা উৎস যাচাই যুক্ত নয়।"
            ],
        )
    if engine in [
        "care",
        "prescription",
        "maternal",
        "home",
        "worksite",
        "road",
        "school",
        "phraseboard",
    ]:
        s = text(p)
        lines = [l.strip() for l in re.split(r"[\n।]+", s) if l.strip()]
        return result(
            "Source-preserving private checklist / নিজের লেখার ব্যক্তিগত তালিকা",
            {"items": len(lines)},
            {"verbatim_items": lines, "location": text(p, "location", False)},
            [
                "Only your text was organized; no diagnosis, safety classification, dose or official submission was generated. / শুধু আপনার লেখা সাজানো হয়েছে।"
            ],
        )
    raise InputError("Unsupported engine / ইঞ্জিনটি পাওয়া যায়নি")
