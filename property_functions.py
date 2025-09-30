# property_functions.py — minimal working version

from typing import Optional, Tuple, List

# --- Helpers ---
def _single_money_to_int(token: str) -> Optional[int]:
    try:
        s = token.strip().lower().replace("$", "").replace(",", "")
        if s.endswith("k"):
            return int(float(s[:-1]) * 1_000)
        if s.endswith("m"):
            return int(float(s[:-1]) * 1_000_000)
        return int(float(s))
    except Exception:
        return None

def _parse_budget_str_to_number(band: str) -> Optional[int]:
    if not band:
        return None
    s = band.lower().replace("$", "").replace(",", "").strip()
    if "–" in s or "-" in s:
        sep = "–" if "–" in s else "-"
        left, right = [x.strip() for x in s.split(sep, 1)]
        l = _single_money_to_int(left)
        r = _single_money_to_int(right)
        if l and r:
            return (l + r) // 2
        return l or r
    return _single_money_to_int(s)

# --- Public functions the agent will call ---

def normalize_budget(budget_band: Optional[str], numeric_budget: Optional[int]) -> Optional[int]:
    """
    Accept either a numeric budget or a string band like '850–950k' or '$900k' and return an int AUD.
    """
    if numeric_budget is not None:
        return numeric_budget
    if budget_band:
        return _parse_budget_str_to_number(budget_band)
    return None

def recommend_by_budget(budget: Optional[int]) -> Tuple[List[str], str]:
    """
    Baseline logic from the brief:
      - budget < 650k → ['1-bed'], with note about limited/extra parking
      - 650k–1.1m → ['1-bed','2-bed']
      - >1.1m → ['2-bed','3-bed'], note: confirm two car spaces
    """
    if budget is None:
        return ([], "No budget provided.")
    if budget < 650_000:
        return (["1-bed"], "Note: parking is limited and costs extra for most 1-beds.")
    if 650_000 <= budget <= 1_100_000:
        return (["1-bed", "2-bed"], "")
    return (["2-bed", "3-bed"], "Confirm two car spaces are required for 3-bed options.")

def answer_faq(user_text: str) -> Optional[str]:
    """
    Strict, hard-coded answers from the fictional knowledge pack.
    Returns None if unknown so the agent can escalate.
    """
    if not user_text:
        return None
    t = user_text.lower()
    if any(k in t for k in ["construction", "complete", "completion", "build", "finish"]):
        return "Start target late 2025; completion targeted Q4 2027 (indicative)."
    if any(k in t for k in ["yield", "rental", "rent", "return"]):
        return "No rental guarantees; we can refer you to a property manager."
    if any(k in t for k in ["firb", "foreign", "overseas", "stamp duty", "surcharge"]):
        return "Foreign buyers may face extra approval/taxes; we can refer, but do not advise."
    if any(k in t for k in ["finance", "broker", "mortgage", "loan", "pre-approval", "pre approved", "preapproved"]):
        return "We can refer you to a broker; no personal finance advice."
    if any(k in t for k in ["finish", "upgrade", "custom"]):
        return "Limited customisation windows, subject to availability/cost."
    if "parking" in t or "car " in t or "carpark" in t:
        return "Parking is limited for 1-beds and paid extra; not guaranteed."
    return None

# === FUNCTION MAP (Deepgram agent will call these by name) ===
FUNCTION_MAP = {
    "recommend_by_budget": lambda budget: {
        "recommended_types": recommend_by_budget(budget)[0],
        "note": recommend_by_budget(budget)[1],
    },
    "answer_faq": lambda user_text: {
        "answer": answer_faq(user_text)  # may be None to trigger escalation
    },
    "normalize_budget": lambda budget_band=None, numeric_budget=None: {
        "normalized_budget": normalize_budget(budget_band, numeric_budget)
    },
    # If you’ve added these already, keep them; otherwise you can add later:
    # "book_appointment": lambda name, phone, email, slot_iso, mode, notes: book_appointment(
    #     name, phone, email, slot_iso, mode, notes
    # ),
    # "summarize_lead": lambda qualification: {"summary": summarize_lead(qualification)},
    # "build_booking_readback": lambda booking_json: {"readback": build_booking_readback(booking_json)},
}
 
