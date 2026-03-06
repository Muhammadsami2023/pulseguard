# utils.py
# Helper functions for PulseGuard

import datetime

# ─────────────────────────────────────────
# RISK LEVEL CALCULATOR
# Takes a score (0-100) and returns
# the risk level, color, and emoji
# ─────────────────────────────────────────
def get_risk_level(score):
    if score >= 70:
        return {
            "level": "LOW RISK",
            "color": "#16A34A",
            "bg": "#DCFCE7",
            "emoji": "🟢",
            "recommendation": "Company shows stable financial signals. Loan can be considered."
        }
    elif score >= 40:
        return {
            "level": "MEDIUM RISK",
            "color": "#CA8A04",
            "bg": "#FEF9C3",
            "emoji": "🟡",
            "recommendation": "Company shows some warning signals. Proceed with caution and extra due diligence."
        }
    else:
        return {
            "level": "HIGH RISK",
            "color": "#DC2626",
            "bg": "#FEE2E2",
            "emoji": "🔴",
            "recommendation": "Company shows multiple stress signals. Loan approval not recommended at this time."
        }


# ─────────────────────────────────────────
# DATE HELPER
# Returns today's date as clean string
# ─────────────────────────────────────────
def get_today():
    return datetime.datetime.now().strftime("%d %B %Y")


# ─────────────────────────────────────────
# SCORE CHANGE DETECTOR
# Tells us if score is going up or down
# ─────────────────────────────────────────
def get_score_trend(old_score, new_score):
    diff = new_score - old_score
    if diff > 5:
        return f"⬆️ Improved by {diff} points"
    elif diff < -5:
        return f"⬇️ Declined by {abs(diff)} points — Monitor Closely"
    else:
        return f"➡️ Stable (change of {diff} points)"


# ─────────────────────────────────────────
# FORMAT CURRENCY
# Converts numbers to readable PKR format
# ─────────────────────────────────────────
def format_pkr(amount):
    if amount is None:
        return "N/A"
    try:
        amount = float(amount)
        if abs(amount) >= 1_000_000_000:
            return f"PKR {amount/1_000_000_000:.2f} Billion"
        elif abs(amount) >= 1_000_000:
            return f"PKR {amount/1_000_000:.2f} Million"
        else:
            return f"PKR {amount:,.0f}"
    except:
        return "N/A"


# ─────────────────────────────────────────
# SAFE DIVIDE
# Prevents division by zero errors
# ─────────────────────────────────────────
def safe_divide(numerator, denominator):
    try:
        if denominator == 0 or denominator is None:
            return 0
        return numerator / denominator
    except:
        return 0


# ─────────────────────────────────────────
# PSX LISTED COMPANIES
# Our initial list of companies we support
# ─────────────────────────────────────────
PSX_COMPANIES = {
    # ── BANKING ──
    "HBL":    "Habib Bank Limited",
    "UBL":    "United Bank Limited",
    "MCB":    "MCB Bank Limited",
    "NBP":    "National Bank of Pakistan",
    "ABL":    "Allied Bank Limited",
    "BAFL":   "Bank Alfalah Limited",
    "MEBL":   "Meezan Bank Limited",
    "BAHL":   "Bank Al Habib Limited",
    "AKBL":   "Askari Bank Limited",
    "FABL":   "Faysal Bank Limited",

    # ── OIL & GAS ──
    "OGDC":   "Oil & Gas Development Company",
    "PPL":    "Pakistan Petroleum Limited",
    "PSO":    "Pakistan State Oil",
    "MARI":   "Mari Petroleum Company",
    "POL":    "Pakistan Oilfields Limited",
    "HASCOL": "Hascol Petroleum Limited",

    # ── CEMENT ──
    "LUCK":   "Lucky Cement",
    "MLCF":   "Maple Leaf Cement",
    "DGKC":   "D.G. Khan Cement",
    "ACPL":   "Attock Cement",
    "PIOC":   "Pioneer Cement",
    "KOHC":   "Kohat Cement",
    "CHCC":   "Cherat Cement",
    "FCCL":   "Fauji Cement Company",

    # ── FERTILIZER ──
    "FFC":    "Fauji Fertilizer Company",
    "FFBL":   "Fauji Fertilizer Bin Qasim",
    "ENGRO":  "Engro Corporation",
    "EFERT":  "Engro Fertilizers Limited",

    # ── POWER ──
    "HUBC":   "Hub Power Company",
    "KAPCO":  "Kot Addu Power Company",
    "NCPL":   "Nishat Chunian Power",
    "NPL":    "Nishat Power Limited",
    "KEL":    "K-Electric Limited",

    # ── TEXTILE ──
    "NML":    "Nishat Mills Limited",
    "NCL":    "Nishat Chunian Limited",
    "GATM":   "Gul Ahmed Textile Mills",
    "KTML":   "Kohinoor Textile Mills",
    "ADMM":   "Adamjee Insurance",

    # ── FOOD & BEVERAGES ──
    "NESTLE": "Nestle Pakistan",
    "UNITY":  "Unity Foods",
    "TREET":  "Treet Corporation",
    "QUICE":  "Quice Food Industries",

    # ── PHARMA ──
    "SEARL":  "The Searle Company",
    "GLAXO":  "GlaxoSmithKline Pakistan",
    "ABOT":   "Abbott Laboratories Pakistan",
    "FEROZ":  "Ferozsons Laboratories",

    # ── CHEMICALS & CONSUMER ──
    "ICI":    "ICI Pakistan",
    "COLG":   "Colgate Palmolive Pakistan",
    "UNILEVER": "Unilever Pakistan",

    # ── TELECOM ──
    "TRG":    "TRG Pakistan Limited",
    "SYS":    "Systems Limited",
    "NETSOL": "NetSol Technologies",

    # ── DIVERSIFIED ──
    "DAWH":   "Dawood Hercules Corporation",
    "DSFL":   "Dewan Sugar Mills",
}


def get_company_name(ticker):
    return PSX_COMPANIES.get(ticker.upper(), ticker.upper())


def get_all_tickers():
    return list(PSX_COMPANIES.keys())