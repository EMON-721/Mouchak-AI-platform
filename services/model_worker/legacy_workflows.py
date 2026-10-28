"""Feature ports from preserved user-owned deployment engines.

Data licenses/attribution stay attached. No browser accounts or storage are merged.
"""

from pathlib import Path
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from decimal import Decimal
import json, re, unicodedata
from .domain import InputError, number, text, result

ROOT = Path(__file__).resolve().parents[2]
READING = json.loads((ROOT / "data/legacy/banglaread-passages.json").read_text())
PRODUCTS = json.loads((ROOT / "data/legacy/commodity-dictionary.json").read_text())
DHAKA = ZoneInfo("Asia/Dhaka")


def canonical(value):
    return re.sub(
        r"\s+",
        " ",
        unicodedata.normalize("NFC", str(value)).replace("য়", "য়").casefold(),
    ).strip()


def reading_reflection(p):
    passage = next((x for x in READING if x["id"] == p.get("passage_id")), None)
    if not passage:
        raise InputError("Choose an available reading passage / পাঠ বেছে নিন")
    selected = p.get("difficult_indices", [])
    words = unicodedata.normalize("NFC", passage["text"]).split()
    if (
        not isinstance(selected, list)
        or len(selected) > len(words)
        or any(type(x) is not int or x < 0 or x >= len(words) for x in selected)
    ):
        raise InputError("Invalid selected word positions / শব্দের অবস্থান সঠিক নয়")
    indices = sorted(set(selected))
    clean = lambda s: re.sub(r"[।,!?;:]", "", unicodedata.normalize("NFC", s)).strip()
    answer = text(p, "answer", False)
    expected = clean(passage["answer"])
    comprehension = (
        "skipped"
        if not answer
        else "matched" if expected in clean(answer) else "review"
    )
    r = result(
        "Tap-and-reflect reading practice / নিজে চিহ্নিত শব্দ ও বোঝার অনুশীলন",
        {
            "passage_id": passage["id"],
            "total_words": len(words),
            "self_marked_difficult_words": list(
                dict.fromkeys(clean(words[i]) for i in indices)
            ),
            "reviewed_words": len(words) - len(indices),
            "comprehension": comprehension,
        },
        {
            "question": passage["question"],
            "your_answer": answer,
            "passage": passage["text"],
        },
        [
            "Self-reported practice, not speech/pronunciation or clinical assessment. / নিজের অনুশীলন; উচ্চারণ বা চিকিৎসাগত মূল্যায়ন নয়।"
        ],
    )
    r["references"] = [
        {
            "id": passage["id"],
            "title": passage["title"],
            "publisher": passage["publisher"],
            "license": passage["license"],
            "kind": "original_authored_legacy",
            "source_date": passage["created_at"],
            "official": False,
        }
    ]
    return r


UNITS = {
    "kg": ("kg", Decimal(1)),
    "g": ("kg", Decimal(".001")),
    "l": ("l", Decimal(1)),
    "ml": ("l", Decimal(".001")),
    "piece": ("piece", Decimal(1)),
    "dozen": ("piece", Decimal(12)),
}


def unit(value):
    key = str(value).casefold()
    if key not in UNITS:
        raise InputError("Use kg/g/l/ml/piece/dozen / সঠিক একক দিন")
    return UNITS[key]


def semantic(row):
    return tuple(
        canonical(row.get(k, default))
        for k, default in [
            ("price_type", "retail"),
            ("grade", "unspecified"),
            ("origin", "unspecified"),
        ]
    )


def product(value):
    q = canonical(value)
    matches = [
        x
        for x in PRODUCTS
        if q in {canonical(x["name"]), *(canonical(a) for a in x.get("aliases", []))}
    ]
    if len(matches) != 1:
        raise InputError(
            "Choose one exact known product or alias / তালিকা থেকে নির্দিষ্ট পণ্য বেছে নিন"
        )
    return matches[0]


def basket_compare(p, now=None):
    clock = now or datetime.now(DHAKA)
    today = clock.astimezone(DHAKA).date()
    days = int(number(p.get("freshness_days", 7), minimum=1, maximum=365))
    basket = p.get("basket")
    offers = p.get("offers")
    if (
        not isinstance(basket, list)
        or not 1 <= len(basket) <= 50
        or not all(isinstance(x, dict) for x in basket)
    ):
        raise InputError("Add 1–50 basket lines / বাজারের তালিকা দিন")
    if (
        not isinstance(offers, list)
        or len(offers) > 200
        or not all(isinstance(x, dict) for x in offers)
    ):
        raise InputError("At most 200 observed offers / সর্বোচ্চ ২০০টি দেখা দাম")
    checked = []
    rejected = []
    for index, o in enumerate(offers):
        try:
            ref = product(o.get("product", ""))
            family, factor = unit(o.get("unit"))
            quantity = number(o.get("quantity"), minimum=".000001")
            price = number(o.get("price"), minimum=".01")
            observed = datetime.strptime(str(o.get("date", "")), "%Y-%m-%d").date()
            if o.get("price_type", "retail") not in ["retail", "wholesale"]:
                raise InputError("Invalid price type")
            if observed > today or clock.astimezone(DHAKA) - datetime.combine(
                observed, time.min, DHAKA
            ) > timedelta(days=days):
                raise InputError(
                    "Stale or future observation / পুরোনো বা ভবিষ্যতের দাম"
                )
            if o.get("flagged") is True:
                raise InputError("Flagged observation / আপত্তিযুক্ত দাম")
            checked.append(
                {
                    "index": index,
                    "product_id": ref["id"],
                    "product": ref["name"],
                    "family": family,
                    "rate": price / (quantity * factor),
                    "semantics": semantic(o),
                    "vendor": text(o, "vendor"),
                    "market": text(o, "market"),
                    "date": str(observed),
                    "source_kind": "private_user_observation",
                }
            )
        except (ValueError, TypeError) as e:
            rejected.append({"row": index + 1, "reason": str(e)})
    lines = []
    known = Decimal(0)
    for item in basket:
        ref = product(item.get("product", ""))
        family, factor = unit(item.get("unit"))
        quantity = number(item.get("quantity"), minimum=".000001")
        matched = [
            o
            for o in checked
            if o["product_id"] == ref["id"]
            and o["family"] == family
            and o["semantics"] == semantic(item)
        ]
        matched.sort(key=lambda x: x["rate"])
        options = [
            {
                "vendor": o["vendor"],
                "market": o["market"],
                "date": o["date"],
                "unit_price_bdt": str(o["rate"].quantize(Decimal(".0001"))),
                "basket_cost_bdt": str(
                    (o["rate"] * quantity * factor).quantize(Decimal(".01"))
                ),
                "source_kind": o["source_kind"],
            }
            for o in matched
        ]
        cost = (
            (matched[0]["rate"] * quantity * factor).quantize(Decimal(".01"))
            if matched
            else None
        )
        if cost is not None:
            known += cost
        lines.append(
            {
                "product": ref["name"],
                "quantity": str(quantity),
                "unit": item["unit"],
                "comparable_offers": options,
                "lowest_observed_cost_bdt": str(cost) if cost is not None else None,
            }
        )
    r = result(
        "Freshness- and grade-matched private basket comparison / তারিখ ও মান মিলিয়ে নিজের বাজারের তুলনা",
        {
            "basket_lines": len(lines),
            "fully_covered": all(
                x["lowest_observed_cost_bdt"] is not None for x in lines
            ),
            "known_lines_subtotal_bdt": str(known.quantize(Decimal(".01"))),
            "missing_prices": [
                x["product"] for x in lines if x["lowest_observed_cost_bdt"] is None
            ],
            "excluded_observations": len(rejected),
        },
        {"lines": lines, "rejected_observations": rejected},
        [
            "User-entered dated observations; no live official market prices or guaranteed shopping total. / নিজের দেখা তারিখসহ দাম; সরাসরি সরকারি বাজারদর বা নিশ্চিত মোট নয়।"
        ],
    )
    r["references"] = [
        {
            "title": "BazarCompare V3 original commodity dictionary",
            "kind": "original_reference_dictionary",
            "publisher": "BazarCompare project authored V3 replacement dictionary",
            "contains_price_data": False,
            "official": False,
        },
        {
            "title": "Your private observations",
            "kind": "user_provided",
            "official": False,
        },
    ]
    return r
