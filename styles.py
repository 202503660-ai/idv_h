"""Editorial visual theme, Plotly styling defaults, and safe UI components
for the World Specialty Coffee Atlas (월드 스페셜티 커피 아틀라스).

Uses only Python standard library modules and Streamlit.
"""

from __future__ import annotations

import html
import math
from typing import Any

import streamlit as st

COFFEE_PALETTE: dict[str, Any] = {
    "background": "#FAF6F0",
    "surface": "#F3ECE1",
    "card": "#FFFDF9",
    "border": "#E6DACB",
    "ink": "#231710",
    "muted": "#6B5648",
    "primary": "#9A4D22",
    "gold": "#C68B59",
    "sage": "#4E6E58",
    "berry": "#8B3A4C",
    "espresso": "#3C2415",
    "sensory_colors": {
        "aroma": "#9A4D22",
        "flavor": "#C68B59",
        "aftertaste": "#6E4730",
        "acidity": "#8B3A4C",
        "body": "#3C2415",
        "balance": "#4E6E58",
    },
    "archetype_colors": {
        "플로럴 · 브라이트": "#C68B59",
        "프루티 · 쥬시": "#8B3A4C",
        "초콜릿 · 풀바디": "#3C2415",
        "스위트 · 클린컵": "#4E6E58",
        "스페셜티 밸런스": "#9A4D22",
    },
    "processing_colors": {
        "워시드 (수세식)": "#4E6E58",
        "내추럴 (건식)": "#8B3A4C",
        "허니 / 펄프드 내추럴": "#C68B59",
        "세미워시드": "#9A4D22",
        "기타 / 미상": "#8C7A6B",
        "Washed / Wet": "#4E6E58",
        "Natural / Dry": "#8B3A4C",
        "Pulped natural / honey": "#C68B59",
        "Semi-washed / Semi-pulped": "#9A4D22",
        "Other / Unknown": "#8C7A6B",
    },
    "species_colors": {
        "Arabica": "#9A4D22",
        "Robusta": "#3C2415",
    },
    "map_colorscale": [
        [0.0, "#F3ECE1"],
        [0.25, "#DEC09E"],
        [0.5, "#C68B59"],
        [0.75, "#9A4D22"],
        [1.0, "#3C2415"],
    ],
}

PLOTLY_LAYOUT_DEFAULTS: dict[str, Any] = {
    "font": {
        "family": "'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Malgun Gothic', sans-serif",
        "size": 13,
        "color": COFFEE_PALETTE["ink"],
    },
    "title_font": {
        "family": "'Playfair Display', 'Noto Serif KR', Georgia, serif",
        "size": 18,
        "color": COFFEE_PALETTE["ink"],
    },
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "colorway": [
        COFFEE_PALETTE["primary"],
        COFFEE_PALETTE["gold"],
        COFFEE_PALETTE["sage"],
        COFFEE_PALETTE["berry"],
        COFFEE_PALETTE["espresso"],
        "#7D5A44",
    ],
    "hoverlabel": {
        "bgcolor": COFFEE_PALETTE["card"],
        "bordercolor": COFFEE_PALETTE["gold"],
        "font": {
            "family": "'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif",
            "size": 13,
            "color": COFFEE_PALETTE["ink"],
        },
    },
    "legend": {
        "bgcolor": "rgba(255,253,249,0.82)",
        "bordercolor": COFFEE_PALETTE["border"],
        "borderwidth": 1,
        "font": {
            "size": 12,
            "color": COFFEE_PALETTE["ink"],
        },
    },
    "margin": {"l": 24, "r": 24, "t": 48, "b": 28},
}

_SENSORY_META: tuple[tuple[str, str, str], ...] = (
    ("aroma", "아로마", "Aroma"),
    ("flavor", "풍미", "Flavor"),
    ("aftertaste", "여운", "Aftertaste"),
    ("acidity", "산미", "Acidity"),
    ("body", "바디감", "Body"),
    ("balance", "밸런스", "Balance"),
)


def _is_missing(value: Any) -> bool:
    """Return True if value is None, NaN, inf, pandas NA/NaT, or empty placeholder text."""
    if value is None:
        return True
    if type(value).__name__ in {"NAType", "NaTType"}:
        return True
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return True
    if isinstance(value, str):
        stripped = value.strip()
        return stripped == "" or stripped.lower() in {"nan", "none", "null", "n/a", "<na>", "nat"}
    if not isinstance(value, bool) and hasattr(value, "__float__"):
        try:
            fval = float(value)
            if math.isnan(fval) or math.isinf(fval):
                return True
        except (TypeError, ValueError):
            pass
    text = str(value).strip().lower()
    return text in {"", "nan", "none", "null", "n/a", "<na>", "nat"}


def _first_present(*values: Any) -> Any:
    """Return the first non-missing value, or None."""
    for value in values:
        if not _is_missing(value):
            return value
    return None


def _esc(value: Any, default: str = "") -> str:
    """Safely convert any value to HTML-escaped string."""
    if _is_missing(value):
        return html.escape(default, quote=True)
    return html.escape(str(value).strip(), quote=True)


def _safe_float(value: Any) -> float | None:
    """Parse a finite float or return None."""
    if _is_missing(value):
        return None
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(num) or math.isinf(num):
        return None
    return num


def _safe_int(value: Any, default: int = 0) -> int:
    """Parse an integer safely or return default."""
    num = _safe_float(value)
    if num is None:
        return default
    return int(round(num))


def _compact_html(markup: str) -> str:
    """Strip leading whitespace and blank lines so st.markdown never parses HTML as code."""
    return "\n".join(line.strip() for line in markup.splitlines() if line.strip())


def _render_html(markup: str) -> None:
    """Render compact, escaped HTML markup via Streamlit."""
    st.markdown(_compact_html(markup), unsafe_allow_html=True)


def _resolve_archetype_color(archetype: str) -> str:
    """Match an archetype label to its palette color with graceful fallback."""
    colors: dict[str, str] = COFFEE_PALETTE["archetype_colors"]
    if archetype in colors:
        return colors[archetype]
    lower = archetype.lower()
    if "플로럴" in archetype or "브라이트" in archetype or "floral" in lower:
        return COFFEE_PALETTE["gold"]
    if "프루티" in archetype or "쥬시" in archetype or "베리" in archetype or "fruit" in lower:
        return COFFEE_PALETTE["berry"]
    if "초콜릿" in archetype or "바디" in archetype or "다크" in archetype or "choc" in lower:
        return COFFEE_PALETTE["espresso"]
    if "스위트" in archetype or "클린" in archetype or "sweet" in lower or "clean" in lower:
        return COFFEE_PALETTE["sage"]
    return COFFEE_PALETTE["primary"]


def _resolve_processing_color(processing: str) -> str:
    """Match a processing method label to its palette color with graceful fallback."""
    colors: dict[str, str] = COFFEE_PALETTE["processing_colors"]
    if processing in colors:
        return colors[processing]
    lower = processing.lower()
    if "워시드" in processing or "washed" in lower or "wet" in lower:
        if "세미" in processing or "semi" in lower:
            return COFFEE_PALETTE["primary"]
        return COFFEE_PALETTE["sage"]
    if "내추럴" in processing or "natural" in lower or "dry" in lower:
        if "허니" in processing or "펄프드" in processing or "honey" in lower or "pulped" in lower:
            return COFFEE_PALETTE["gold"]
        return COFFEE_PALETTE["berry"]
    if "허니" in processing or "honey" in lower:
        return COFFEE_PALETTE["gold"]
    return "#8C7A6B"


def _cup_grade_label(score: float | None) -> str:
    """Return CQI specialty tier label for a given 100-point cup score."""
    if score is None:
        return "CQI ARCHIVE"
    if score >= 90.0:
        return "OUTSTANDING"
    if score >= 85.0:
        return "EXCELLENT"
    if score >= 80.0:
        return "VERY GOOD"
    return "CQI GRADED"


def inject_custom_css() -> None:
    """Inject editorial magazine CSS for the World Specialty Coffee Atlas."""
    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=Noto+Serif+KR:wght@500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&display=swap');

:root {{
    --coffee-bg: {COFFEE_PALETTE["background"]};
    --coffee-surface: {COFFEE_PALETTE["surface"]};
    --coffee-card: {COFFEE_PALETTE["card"]};
    --coffee-border: {COFFEE_PALETTE["border"]};
    --coffee-ink: {COFFEE_PALETTE["ink"]};
    --coffee-muted: {COFFEE_PALETTE["muted"]};
    --coffee-primary: {COFFEE_PALETTE["primary"]};
    --coffee-gold: {COFFEE_PALETTE["gold"]};
    --coffee-sage: {COFFEE_PALETTE["sage"]};
    --coffee-berry: {COFFEE_PALETTE["berry"]};
    --coffee-espresso: {COFFEE_PALETTE["espresso"]};
    --font-serif: 'Playfair Display', 'Noto Serif KR', Georgia, 'Times New Roman', serif;
    --font-sans: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Malgun Gothic', sans-serif;
}}

html, body, .stApp {{
    background-color: var(--coffee-bg);
    color: var(--coffee-ink);
    font-family: var(--font-sans);
}}

.stApp {{
    background-image:
        radial-gradient(ellipse 80% 45% at 88% 0%, rgba(198, 139, 89, 0.11), transparent 60%),
        radial-gradient(ellipse 65% 40% at 8% 12%, rgba(78, 110, 88, 0.05), transparent 55%);
    background-attachment: scroll;
}}

/* Keep Streamlit header & sidebar toggle visible and harmoniously tinted */
header[data-testid="stHeader"] {{
    background: rgba(250, 246, 240, 0.86);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(230, 218, 203, 0.65);
}}

.block-container,
[data-testid="stMainBlockContainer"] {{
    max-width: 1240px;
    padding-top: 2.2rem;
    padding-bottom: 3.5rem;
}}

h1, h2, h3, h4 {{
    font-family: var(--font-serif);
    color: var(--coffee-ink);
    letter-spacing: -0.015em;
}}

p, li, label, .stMarkdown {{
    font-family: var(--font-sans);
}}

/* Sidebar Editorial Polish */
section[data-testid="stSidebar"] {{
    background-color: var(--coffee-surface);
    border-right: 1px solid var(--coffee-border);
}}

section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
    padding-top: 1.5rem;
}}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    font-family: var(--font-serif);
    color: var(--coffee-ink);
}}

section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] input {{
    background-color: var(--coffee-card);
    border-color: var(--coffee-border);
    border-radius: 8px;
}}

section[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background-color: rgba(154, 77, 34, 0.12);
    color: var(--coffee-ink);
    border: 1px solid rgba(154, 77, 34, 0.28);
    border-radius: 6px;
}}

/* Tabs Polish */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.4rem;
    border-bottom: 1px solid var(--coffee-border);
    background-color: transparent;
    padding-bottom: 0;
}}

.stTabs [data-baseweb="tab"] {{
    font-family: var(--font-sans);
    font-weight: 500;
    font-size: 0.94rem;
    color: var(--coffee-muted);
    background-color: transparent;
    border-radius: 8px 8px 0 0;
    padding: 0.65rem 1.15rem;
    transition: color 0.18s ease, background-color 0.18s ease;
}}

.stTabs [data-baseweb="tab"]:hover {{
    color: var(--coffee-ink);
    background-color: rgba(243, 236, 225, 0.72);
}}

.stTabs [aria-selected="true"] {{
    color: var(--coffee-primary) !important;
    font-weight: 700 !important;
    background-color: rgba(255, 253, 249, 0.9) !important;
}}

.stTabs [data-baseweb="tab-highlight"] {{
    background-color: var(--coffee-primary) !important;
    height: 2.5px !important;
}}

/* Buttons & Download Buttons */
.stButton > button,
.stDownloadButton > button {{
    font-family: var(--font-sans);
    font-weight: 600;
    font-size: 0.88rem;
    letter-spacing: 0.01em;
    color: var(--coffee-ink);
    background-color: var(--coffee-card);
    border: 1px solid var(--coffee-gold);
    border-radius: 999px;
    padding: 0.5rem 1.25rem;
    box-shadow: 0 2px 8px rgba(35, 23, 16, 0.05);
    transition: all 0.2s ease;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    background-color: var(--coffee-primary);
    color: #FAF6F0;
    border-color: var(--coffee-primary);
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(154, 77, 34, 0.22);
}}

.stButton > button:focus,
.stDownloadButton > button:focus {{
    box-shadow: 0 0 0 3px rgba(154, 77, 34, 0.22);
}}

/* Expanders, Metrics, DataFrames, Alerts */
[data-testid="stExpander"] {{
    background-color: var(--coffee-card);
    border: 1px solid var(--coffee-border);
    border-radius: 12px;
    overflow: hidden;
}}

[data-testid="stMetric"] {{
    background-color: var(--coffee-card);
    border: 1px solid var(--coffee-border);
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    box-shadow: 0 3px 14px rgba(35, 23, 16, 0.035);
}}

[data-testid="stDataFrame"] {{
    border: 1px solid var(--coffee-border);
    border-radius: 12px;
    overflow: hidden;
}}

[data-testid="stAlert"] {{
    border-radius: 12px;
    border: 1px solid var(--coffee-border);
}}

/* Hero Editorial Banner */
.coffee-hero {{
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #231710 0%, #372014 54%, #522E1A 100%);
    color: #FAF6F0;
    border: 1px solid rgba(198, 139, 89, 0.42);
    border-radius: 20px;
    padding: 2.4rem 2.6rem 2rem 2.6rem;
    margin-bottom: 1.8rem;
    box-shadow: 0 18px 42px rgba(35, 23, 16, 0.16);
}}

.coffee-hero-ornament {{
    position: absolute;
    top: -18px;
    right: -12px;
    width: 340px;
    height: 340px;
    opacity: 0.11;
    pointer-events: none;
}}

.coffee-hero-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-bottom: 1.15rem;
    position: relative;
    z-index: 1;
}}

.coffee-hero-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-family: var(--font-sans);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #F3DCC1;
    background: rgba(198, 139, 89, 0.16);
    border: 1px solid rgba(198, 139, 89, 0.45);
    border-radius: 999px;
    padding: 0.34rem 0.9rem;
}}

.coffee-hero-edition {{
    font-family: var(--font-sans);
    font-size: 0.74rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(250, 246, 240, 0.68);
}}

.coffee-hero-title {{
    font-family: 'Noto Serif KR', 'Playfair Display', Georgia, serif;
    font-size: clamp(1.85rem, 3.5vw, 2.75rem);
    font-weight: 700;
    line-height: 1.2;
    color: #FAF6F0;
    margin: 0 0 0.45rem 0;
    position: relative;
    z-index: 1;
}}

.coffee-hero-en {{
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic;
    font-size: clamp(1rem, 1.55vw, 1.24rem);
    font-weight: 500;
    color: #E2B88C;
    margin: 0 0 1rem 0;
    position: relative;
    z-index: 1;
}}

.coffee-hero-desc {{
    font-family: var(--font-sans);
    font-size: 0.95rem;
    line-height: 1.72;
    color: rgba(250, 246, 240, 0.86);
    max-width: 720px;
    margin: 0 0 1.75rem 0;
    position: relative;
    z-index: 1;
}}

.coffee-hero-stats {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.2rem;
    padding-top: 1.35rem;
    border-top: 1px solid rgba(230, 218, 203, 0.22);
    position: relative;
    z-index: 1;
}}

.coffee-hero-stat-label {{
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #D7AF86;
    margin-bottom: 0.28rem;
}}

.coffee-hero-stat-value {{
    font-family: 'Playfair Display', 'Noto Serif KR', Georgia, serif;
    font-size: clamp(1.45rem, 2.4vw, 1.95rem);
    font-weight: 700;
    line-height: 1.15;
    color: #FAF6F0;
}}

.coffee-hero-stat-unit {{
    font-family: var(--font-sans);
    font-size: 0.84rem;
    font-weight: 400;
    color: rgba(250, 246, 240, 0.72);
    margin-left: 0.25rem;
}}

.coffee-hero-stat-sub {{
    font-size: 0.8rem;
    color: rgba(250, 246, 240, 0.72);
    margin-top: 0.2rem;
}}

/* Editorial Section Header */
.coffee-section-header {{
    margin: 2.15rem 0 1.25rem 0;
    padding-bottom: 0.85rem;
    border-bottom: 1px solid var(--coffee-border);
}}

.coffee-section-eyebrow {{
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    font-family: var(--font-sans);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--coffee-primary);
    margin-bottom: 0.42rem;
}}

.coffee-section-eyebrow::before {{
    content: "";
    display: inline-block;
    width: 24px;
    height: 1.5px;
    background-color: var(--coffee-gold);
}}

.coffee-section-title {{
    font-family: 'Noto Serif KR', 'Playfair Display', Georgia, serif;
    font-size: clamp(1.3rem, 2.2vw, 1.68rem);
    font-weight: 700;
    line-height: 1.3;
    color: var(--coffee-ink);
    margin: 0;
}}

.coffee-section-subtitle {{
    font-family: var(--font-sans);
    font-size: 0.93rem;
    line-height: 1.65;
    color: var(--coffee-muted);
    max-width: 760px;
    margin: 0.45rem 0 0 0;
}}

/* KPI Strip */
.coffee-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
    gap: 1rem;
    margin: 0.6rem 0 1.4rem 0;
}}

.coffee-kpi-card {{
    background-color: var(--coffee-card);
    border: 1px solid var(--coffee-border);
    border-top: 3px solid var(--kpi-accent, var(--coffee-gold));
    border-radius: 14px;
    padding: 1.15rem 1.25rem;
    box-shadow: 0 4px 18px rgba(35, 23, 16, 0.04);
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}}

.coffee-kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(35, 23, 16, 0.075);
}}

.coffee-kpi-label {{
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--coffee-muted);
    margin-bottom: 0.42rem;
}}

.coffee-kpi-value {{
    font-family: 'Playfair Display', 'Noto Serif KR', Georgia, serif;
    font-size: clamp(1.45rem, 2.1vw, 1.85rem);
    font-weight: 700;
    line-height: 1.18;
    color: var(--coffee-ink);
    word-break: break-word;
}}

.coffee-kpi-sub {{
    font-size: 0.82rem;
    line-height: 1.45;
    color: var(--coffee-muted);
    margin-top: 0.35rem;
}}

/* Callout Card */
.coffee-callout {{
    background: linear-gradient(135deg, #FFFDF9 0%, #F5EFE5 100%);
    border: 1px solid var(--coffee-border);
    border-left: 4px solid var(--coffee-primary);
    border-radius: 12px;
    padding: 1.15rem 1.35rem;
    margin: 0.75rem 0 1.25rem 0;
    box-shadow: 0 4px 14px rgba(35, 23, 16, 0.035);
}}

.coffee-callout-head {{
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin-bottom: 0.45rem;
}}

.coffee-callout-badge {{
    display: inline-block;
    font-size: 0.71rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--coffee-primary);
    background-color: rgba(154, 77, 34, 0.11);
    border: 1px solid rgba(154, 77, 34, 0.24);
    border-radius: 999px;
    padding: 0.18rem 0.65rem;
}}

.coffee-callout-title {{
    font-family: 'Noto Serif KR', 'Playfair Display', Georgia, serif;
    font-size: 1.06rem;
    font-weight: 700;
    color: var(--coffee-ink);
    margin: 0;
}}

.coffee-callout-body {{
    font-size: 0.91rem;
    line-height: 1.68;
    color: var(--coffee-muted);
    margin: 0;
}}

/* Boutique Roastery Tasting Card */
.coffee-bean-card {{
    background-color: var(--coffee-card);
    border: 1px solid var(--coffee-border);
    border-radius: 16px;
    padding: 1.35rem 1.45rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 6px 22px rgba(35, 23, 16, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}}

.coffee-bean-card:hover {{
    transform: translateY(-2px);
    border-color: rgba(198, 139, 89, 0.75);
    box-shadow: 0 12px 28px rgba(35, 23, 16, 0.09);
}}

.coffee-bean-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    padding-bottom: 0.95rem;
    border-bottom: 1px dashed var(--coffee-border);
}}

.coffee-bean-origin-eyebrow {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--coffee-primary);
    margin-bottom: 0.25rem;
}}

.coffee-bean-country {{
    font-family: 'Noto Serif KR', 'Playfair Display', Georgia, serif;
    font-size: 1.32rem;
    font-weight: 700;
    line-height: 1.25;
    color: var(--coffee-ink);
    margin: 0;
}}

.coffee-bean-place {{
    font-size: 0.85rem;
    color: var(--coffee-muted);
    margin-top: 0.25rem;
    line-height: 1.45;
}}

.coffee-bean-score-box {{
    flex-shrink: 0;
    text-align: center;
    background: linear-gradient(145deg, #231710 0%, #3F2416 100%);
    color: #FAF6F0;
    border: 1px solid rgba(198, 139, 89, 0.55);
    border-radius: 12px;
    padding: 0.55rem 0.9rem;
    min-width: 88px;
}}

.coffee-bean-score-num {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.05;
    color: #F6DFC3;
}}

.coffee-bean-score-tier {{
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #D7AF86;
    margin-top: 0.22rem;
}}

.coffee-bean-specs {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem 0.85rem;
    background-color: #F7F1E8;
    border: 1px solid rgba(230, 218, 203, 0.85);
    border-radius: 10px;
    padding: 0.78rem 0.9rem;
    margin: 0.9rem 0;
}}

.coffee-bean-spec-label {{
    font-size: 0.67rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--coffee-muted);
    margin-bottom: 0.18rem;
}}

.coffee-bean-spec-value {{
    font-size: 0.84rem;
    font-weight: 600;
    color: var(--coffee-ink);
    line-height: 1.35;
    word-break: break-word;
}}

.coffee-proc-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 0.35rem;
    vertical-align: middle;
}}

.coffee-bean-tasting {{
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    padding: 0.75rem 0.95rem;
    border-radius: 10px;
    background-color: rgba(250, 246, 240, 0.85);
    border: 1px solid var(--coffee-border);
    margin-bottom: 0.95rem;
}}

.coffee-bean-tasting-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
}}

.coffee-tasting-kicker {{
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: var(--coffee-muted);
}}

.coffee-archetype-pill {{
    display: inline-flex;
    align-items: center;
    font-size: 0.74rem;
    font-weight: 700;
    color: #FFFDF9;
    border-radius: 999px;
    padding: 0.2rem 0.72rem;
    letter-spacing: 0.02em;
}}

.coffee-bean-notes {{
    font-family: 'Noto Serif KR', Georgia, serif;
    font-size: 0.93rem;
    font-weight: 500;
    line-height: 1.55;
    color: var(--coffee-ink);
}}

.coffee-sensory-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.55rem 1.25rem;
}}

.coffee-sensory-row {{
    display: flex;
    flex-direction: column;
    gap: 0.22rem;
}}

.coffee-sensory-meta {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 0.78rem;
}}

.coffee-sensory-name {{
    color: var(--coffee-muted);
    font-weight: 500;
}}

.coffee-sensory-name.is-top {{
    color: var(--coffee-ink);
    font-weight: 700;
}}

.coffee-sensory-val {{
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 700;
    color: var(--coffee-ink);
    font-size: 0.84rem;
}}

.coffee-sensory-track {{
    width: 100%;
    height: 6px;
    border-radius: 999px;
    background-color: #EFE6D9;
    overflow: hidden;
}}

.coffee-sensory-fill {{
    height: 100%;
    border-radius: 999px;
}}

/* Editorial Coffee Guide (3-Card Grid) */
.coffee-guide-grid {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.15rem;
    margin: 0.8rem 0 1.6rem 0;
}}

.coffee-guide-card {{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: var(--coffee-card);
    border: 1px solid var(--coffee-border);
    border-radius: 16px;
    padding: 1.4rem 1.45rem;
    box-shadow: 0 5px 18px rgba(35, 23, 16, 0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}}

.coffee-guide-card:hover {{
    transform: translateY(-3px);
    border-color: rgba(198, 139, 89, 0.72);
    box-shadow: 0 12px 26px rgba(35, 23, 16, 0.08);
}}

.coffee-guide-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.85rem;
}}

.coffee-guide-num {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.55rem;
    font-weight: 700;
    line-height: 1;
    color: var(--coffee-gold);
}}

.coffee-guide-icon {{
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background-color: var(--coffee-surface);
    border: 1px solid var(--coffee-border);
    display: inline-flex;
    align-items: center;
    justify-content: center;
}}

.coffee-guide-kicker {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: var(--coffee-primary);
    margin-bottom: 0.3rem;
}}

.coffee-guide-title {{
    font-family: 'Noto Serif KR', 'Playfair Display', Georgia, serif;
    font-size: 1.16rem;
    font-weight: 700;
    line-height: 1.35;
    color: var(--coffee-ink);
    margin: 0 0 0.65rem 0;
}}

.coffee-guide-text {{
    font-size: 0.88rem;
    line-height: 1.72;
    color: var(--coffee-muted);
    margin: 0 0 1.1rem 0;
}}

.coffee-guide-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.42rem;
    padding-top: 0.85rem;
    border-top: 1px solid rgba(230, 218, 203, 0.75);
}}

.coffee-guide-tag {{
    font-size: 0.74rem;
    font-weight: 600;
    color: var(--coffee-ink);
    background-color: var(--coffee-surface);
    border: 1px solid var(--coffee-border);
    border-radius: 999px;
    padding: 0.22rem 0.65rem;
}}

/* Editorial Footer */
.coffee-footer {{
    margin-top: 3rem;
    padding: 1.65rem 0 0.75rem 0;
    border-top: 1px solid var(--coffee-border);
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 1rem;
    color: var(--coffee-muted);
}}

.coffee-footer-brand {{
    font-family: 'Noto Serif KR', 'Playfair Display', Georgia, serif;
    font-size: 1.02rem;
    font-weight: 700;
    color: var(--coffee-ink);
    margin-bottom: 0.28rem;
}}

.coffee-footer-meta {{
    font-size: 0.82rem;
    line-height: 1.6;
    color: var(--coffee-muted);
}}

.coffee-footer-link {{
    color: var(--coffee-primary) !important;
    font-weight: 600;
    text-decoration: none;
    border-bottom: 1px solid rgba(154, 77, 34, 0.35);
    transition: border-color 0.18s ease;
}}

.coffee-footer-link:hover {{
    border-bottom-color: var(--coffee-primary);
}}

/* Responsive Adjustments */
@media (max-width: 960px) {{
    .coffee-guide-grid {{
        grid-template-columns: 1fr;
    }}
    .coffee-bean-specs {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
}}

@media (max-width: 680px) {{
    .coffee-hero {{
        padding: 1.6rem 1.35rem 1.4rem 1.35rem;
        border-radius: 16px;
    }}
    .coffee-hero-stats {{
        grid-template-columns: 1fr;
        gap: 0.9rem;
    }}
    .coffee-sensory-grid {{
        grid-template-columns: 1fr;
    }}
    .coffee-bean-header {{
        flex-direction: column;
    }}
    .coffee-bean-score-box {{
        align-self: flex-start;
    }}
}}
</style>
"""
    _render_html(css)


def render_hero(total_beans: int, total_countries: int, avg_score: float) -> None:
    """Render the magazine-grade editorial hero banner with live dataset metrics."""
    beans_int = _safe_int(total_beans, 0)
    countries_int = _safe_int(total_countries, 0)
    score_val = _safe_float(avg_score)
    score_display = f"{score_val:.2f}" if score_val is not None else "—"

    hero_html = f"""
<section class="coffee-hero">
  <svg class="coffee-hero-ornament" viewBox="0 0 320 320" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <circle cx="180" cy="140" r="128" stroke="#E2B88C" stroke-width="1.2" stroke-dasharray="4 6"/>
    <circle cx="180" cy="140" r="96" stroke="#E2B88C" stroke-width="1"/>
    <circle cx="180" cy="140" r="64" stroke="#E2B88C" stroke-width="0.9"/>
    <path d="M52 140H308M180 12V268" stroke="#E2B88C" stroke-width="0.8"/>
    <path d="M90 88C138 118 222 118 270 88M90 192C138 162 222 162 270 192" stroke="#E2B88C" stroke-width="0.9"/>
  </svg>
  <div class="coffee-hero-top">
    <span class="coffee-hero-pill">WORLD SPECIALTY COFFEE ATLAS</span>
    <span class="coffee-hero-edition">CQI CUPPING ARCHIVE · ORIGIN &amp; SENSORY EDITION</span>
  </div>
  <h1 class="coffee-hero-title">월드 스페셜티 커피 아틀라스</h1>
  <p class="coffee-hero-en">World Specialty Coffee Atlas — Terroir, Processing &amp; Sensory Architecture</p>
  <p class="coffee-hero-desc">
    국제 커피 품질 연구소(CQI)의 전문 커핑 데이터를 바탕으로 세계 커피 벨트 산지, 재배 고도, 가공방식,
    그리고 한 잔 속에 담긴 6대 관능 프로파일을 탐험하는 인터랙티브 스페셜티 커피 도감입니다.
  </p>
  <div class="coffee-hero-stats">
    <div>
      <div class="coffee-hero-stat-label">CURATED COFFEE LOTS</div>
      <div class="coffee-hero-stat-value">{_esc(f"{beans_int:,}")}<span class="coffee-hero-stat-unit">종</span></div>
      <div class="coffee-hero-stat-sub">CQI 공식 커핑 평가 완료 원두</div>
    </div>
    <div>
      <div class="coffee-hero-stat-label">ORIGIN NATIONS</div>
      <div class="coffee-hero-stat-value">{_esc(f"{countries_int:,}")}<span class="coffee-hero-stat-unit">개국</span></div>
      <div class="coffee-hero-stat-sub">세계 커피 벨트 주요 생산국</div>
    </div>
    <div>
      <div class="coffee-hero-stat-label">MEAN CUP SCORE</div>
      <div class="coffee-hero-stat-value">{_esc(score_display)}<span class="coffee-hero-stat-unit">/ 100</span></div>
      <div class="coffee-hero-stat-sub">현재 필터 기준 평균 커핑 점수</div>
    </div>
  </div>
</section>
"""
    _render_html(hero_html)


def render_kpi_strip(items: list[dict]) -> None:
    """Render a horizontal strip of refined KPI cards.

    Each item dict supports:
        - label (str): metric title
        - value (str): primary formatted metric value
        - sub (str, optional): short explanatory subtitle
    """
    if not items:
        return

    accents = (
        COFFEE_PALETTE["primary"],
        COFFEE_PALETTE["gold"],
        COFFEE_PALETTE["sage"],
        COFFEE_PALETTE["berry"],
    )
    cards: list[str] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        label = _esc(item.get("label"), "지표")
        value = _esc(item.get("value"), "—")
        sub = _esc(item.get("sub"), "")
        accent = accents[idx % len(accents)]
        sub_html = f'<div class="coffee-kpi-sub">{sub}</div>' if sub else ""
        cards.append(
            f'<div class="coffee-kpi-card" style="--kpi-accent: {accent};">'
            f'<div class="coffee-kpi-label">{label}</div>'
            f'<div class="coffee-kpi-value">{value}</div>'
            f"{sub_html}"
            f"</div>"
        )

    if cards:
        _render_html(f'<div class="coffee-kpi-grid">{"".join(cards)}</div>')


def render_section_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    """Render an editorial section divider with eyebrow, serif title, and optional subtitle."""
    eyebrow_esc = _esc(eyebrow)
    title_esc = _esc(title)
    subtitle_esc = _esc(subtitle)
    eyebrow_html = (
        f'<div class="coffee-section-eyebrow">{eyebrow_esc}</div>' if eyebrow_esc else ""
    )
    subtitle_html = (
        f'<p class="coffee-section-subtitle">{subtitle_esc}</p>' if subtitle_esc else ""
    )
    markup = f"""
<div class="coffee-section-header">
  {eyebrow_html}
  <h2 class="coffee-section-title">{title_esc}</h2>
  {subtitle_html}
</div>
"""
    _render_html(markup)


def render_callout_card(title: str, body: str, badge: str = "") -> None:
    """Render a warm editorial callout/insight card with optional category badge."""
    title_esc = _esc(title)
    body_esc = _esc(body).replace("\n", "<br>")
    badge_esc = _esc(badge)
    badge_html = f'<span class="coffee-callout-badge">{badge_esc}</span>' if badge_esc else ""
    markup = f"""
<div class="coffee-callout">
  <div class="coffee-callout-head">
    {badge_html}
    <h3 class="coffee-callout-title">{title_esc}</h3>
  </div>
  <p class="coffee-callout-body">{body_esc}</p>
</div>
"""
    _render_html(markup)


def render_bean_card(bean: dict) -> None:
    """Render a boutique roastery single-origin tasting card from a bean record dict."""
    if not isinstance(bean, dict):
        return

    country_ko = _esc(_first_present(bean.get("country_ko"), bean.get("country")), "산지 미상")
    species = _esc(bean.get("species"), "Arabica")
    variety = _esc(bean.get("variety"), "품종 미상")

    raw_processing = _first_present(bean.get("processing_ko"), bean.get("processing_method"))
    processing_text = _esc(raw_processing, "가공방식 미상")
    proc_color = _resolve_processing_color(str(raw_processing) if not _is_missing(raw_processing) else "")

    place_parts: list[str] = []
    for key in ("region", "farm_name"):
        val = bean.get(key)
        if not _is_missing(val):
            cleaned = str(val).strip()
            if cleaned and cleaned.lower() not in {"unknown", "nan"} and cleaned not in place_parts:
                place_parts.append(cleaned)
    if not place_parts and not _is_missing(bean.get("producer")):
        place_parts.append(str(bean.get("producer")).strip())
    place_text = _esc(" · ".join(place_parts), "단일 산지 스페셜티 롯트")

    harvest_val = bean.get("harvest_year")
    harvest_suffix = ""
    if not _is_missing(harvest_val):
        harvest_str = str(harvest_val).strip()
        if harvest_str.endswith(".0"):
            harvest_str = harvest_str[:-2]
        if harvest_str:
            harvest_suffix = f" · HARVEST {_esc(harvest_str)}"

    altitude_val = _safe_float(bean.get("altitude_m"))
    altitude_text = _esc(f"{altitude_val:,.0f} m") if altitude_val is not None else "고도 정보 없음"

    cup_score = _safe_float(bean.get("total_cup_points"))
    score_text = f"{cup_score:.2f}" if cup_score is not None else "—"
    grade_tier = _cup_grade_label(cup_score)

    raw_archetype = bean.get("flavor_archetype")
    archetype_str = str(raw_archetype).strip() if not _is_missing(raw_archetype) else "스페셜티 밸런스"
    archetype_esc = _esc(archetype_str)
    archetype_bg = _resolve_archetype_color(archetype_str)

    notes_esc = _esc(
        bean.get("flavor_notes_ko"),
        "균형 잡힌 단맛과 깔끔한 여운이 어우러진 스페셜티 컵 프로파일",
    )

    sensory_items: list[tuple[str, str, str, float]] = []
    for col, label_ko, label_en in _SENSORY_META:
        score = _safe_float(bean.get(col))
        if score is not None:
            sensory_items.append((col, label_ko, label_en, score))

    top_cols: set[str] = set()
    if sensory_items:
        ranked = sorted(sensory_items, key=lambda item: item[3], reverse=True)
        top_cols = {item[0] for item in ranked[:2]}

    sensory_colors: dict[str, str] = COFFEE_PALETTE["sensory_colors"]
    bars_html_parts: list[str] = []
    for col, label_ko, label_en, score in sensory_items:
        pct = max(8.0, min(100.0, ((score - 5.0) / 5.0) * 100.0))
        bar_color = sensory_colors.get(col, COFFEE_PALETTE["primary"])
        is_top = col in top_cols
        name_cls = "coffee-sensory-name is-top" if is_top else "coffee-sensory-name"
        star_mark = " ★" if is_top else ""
        bars_html_parts.append(
            f'<div class="coffee-sensory-row">'
            f'<div class="coffee-sensory-meta">'
            f'<span class="{name_cls}" title="{_esc(label_en)}">{_esc(label_ko)}{star_mark}</span>'
            f'<span class="coffee-sensory-val">{score:.2f}</span>'
            f"</div>"
            f'<div class="coffee-sensory-track">'
            f'<div class="coffee-sensory-fill" style="width: {pct:.1f}%; background-color: {bar_color};"></div>'
            f"</div>"
            f"</div>"
        )

    sensory_section = (
        f'<div class="coffee-sensory-grid">{"".join(bars_html_parts)}</div>'
        if bars_html_parts
        else ""
    )

    card_html = f"""
<article class="coffee-bean-card">
  <div class="coffee-bean-header">
    <div>
      <div class="coffee-bean-origin-eyebrow">{species} · SINGLE ORIGIN{harvest_suffix}</div>
      <h3 class="coffee-bean-country">{country_ko}</h3>
      <div class="coffee-bean-place">{place_text}</div>
    </div>
    <div class="coffee-bean-score-box">
      <div class="coffee-bean-score-num">{_esc(score_text)}</div>
      <div class="coffee-bean-score-tier">{_esc(grade_tier)}</div>
    </div>
  </div>
  <div class="coffee-bean-specs">
    <div>
      <div class="coffee-bean-spec-label">품종 · VARIETY</div>
      <div class="coffee-bean-spec-value">{variety}</div>
    </div>
    <div>
      <div class="coffee-bean-spec-label">가공방식 · PROCESS</div>
      <div class="coffee-bean-spec-value"><span class="coffee-proc-dot" style="background-color: {proc_color};"></span>{processing_text}</div>
    </div>
    <div>
      <div class="coffee-bean-spec-label">재배 고도 · ALTITUDE</div>
      <div class="coffee-bean-spec-value">{altitude_text}</div>
    </div>
    <div>
      <div class="coffee-bean-spec-label">종 · SPECIES</div>
      <div class="coffee-bean-spec-value">{species}</div>
    </div>
  </div>
  <div class="coffee-bean-tasting">
    <div class="coffee-bean-tasting-top">
      <span class="coffee-tasting-kicker">ROASTERY TASTING NOTES</span>
      <span class="coffee-archetype-pill" style="background-color: {archetype_bg};">{archetype_esc}</span>
    </div>
    <div class="coffee-bean-notes">{notes_esc}</div>
  </div>
  {sensory_section}
</article>
"""
    _render_html(card_html)


def render_coffee_guide() -> None:
    """Render the 3-card editorial Specialty Coffee introductory guide."""
    guide_html = f"""
<div class="coffee-guide-grid">
  <article class="coffee-guide-card">
    <div>
      <div class="coffee-guide-top">
        <span class="coffee-guide-num">01</span>
        <span class="coffee-guide-icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{COFFEE_PALETTE["primary"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"/>
            <path d="M3.6 9h16.8M3.6 15h16.8M12 3a13.5 13.5 0 0 1 0 18M12 3a13.5 13.5 0 0 0 0 18"/>
          </svg>
        </span>
      </div>
      <div class="coffee-guide-kicker">COFFEE BELT &amp; TERROIR</div>
      <h3 class="coffee-guide-title">커피 벨트와 테루아</h3>
      <p class="coffee-guide-text">
        스페셜티 커피는 적도 기준 남·북위 25도 사이의 '커피 벨트'에서 태어납니다.
        해발 1,200m 이상 고지대의 서늘한 밤과 따뜻한 낮의 일교차, 미네랄이 풍부한 화산토는
        체리의 숙성을 천천히 이끌어 생두 밀도를 높이고 복합적인 산미와 향미를 완성합니다.
      </p>
    </div>
    <div class="coffee-guide-tags">
      <span class="coffee-guide-tag">적도 남·북위 25°</span>
      <span class="coffee-guide-tag">고도 1,200–2,200m</span>
      <span class="coffee-guide-tag">화산토 · 일교차</span>
    </div>
  </article>

  <article class="coffee-guide-card">
    <div>
      <div class="coffee-guide-top">
        <span class="coffee-guide-num">02</span>
        <span class="coffee-guide-icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{COFFEE_PALETTE["sage"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3c4.5 0 8 4 8 9s-3.5 9-8 9-8-4-8-9 3.5-9 8-9Z"/>
            <path d="M12 3c-1.8 4.2 1.8 13.8 0 18"/>
          </svg>
        </span>
      </div>
      <div class="coffee-guide-kicker">ARABICA VS. ROBUSTA</div>
      <h3 class="coffee-guide-title">아라비카 vs 로부스타</h3>
      <p class="coffee-guide-text">
        아라비카(Arabica)는 고지대 재배에 섬세한 꽃·과일 아로마와 세련된 산미를 지녀
        스페셜티 커피의 중심을 이룹니다. 반면 로부스타(Robusta)는 병충해에 강하고 카페인 함량이 높으며,
        다크 초콜릿·견과류의 묵직한 바디와 풍성한 크레마로 에스프레소 블렌드에 깊이를 더합니다.
      </p>
    </div>
    <div class="coffee-guide-tags">
      <span class="coffee-guide-tag">Arabica · 섬세한 산미</span>
      <span class="coffee-guide-tag">Robusta · 묵직한 바디</span>
      <span class="coffee-guide-tag">CQI 80점+ 스페셜티</span>
    </div>
  </article>

  <article class="coffee-guide-card">
    <div>
      <div class="coffee-guide-top">
        <span class="coffee-guide-num">03</span>
        <span class="coffee-guide-icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{COFFEE_PALETTE["berry"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
          </svg>
        </span>
      </div>
      <div class="coffee-guide-kicker">POST-HARVEST PROCESSING</div>
      <h3 class="coffee-guide-title">가공방식: 워시드 · 내추럴 · 허니</h3>
      <p class="coffee-guide-text">
        수확한 체리에서 과육을 분리하고 건조하는 과정은 향미의 방향을 결정합니다.
        워시드(Washed)는 투명한 산미와 깔끔한 클린컵을, 내추럴(Natural)은 과육째 건조해 농축된 베리·열대과일 단맛을,
        허니(Honey)는 점액질을 남겨 부드러운 꿀 단맛과 라운드한 질감을 표현합니다.
      </p>
    </div>
    <div class="coffee-guide-tags">
      <span class="coffee-guide-tag">Washed · 투명한 산미</span>
      <span class="coffee-guide-tag">Natural · 풍부한 과일향</span>
      <span class="coffee-guide-tag">Honey · 균형 잡힌 단맛</span>
    </div>
  </article>
</div>
"""
    _render_html(guide_html)


def render_footer() -> None:
    """Render the editorial footer with CQI Coffee Quality Database attribution."""
    footer_html = """
<footer class="coffee-footer">
  <div>
    <div class="coffee-footer-brand">월드 스페셜티 커피 아틀라스 · World Specialty Coffee Atlas</div>
    <div class="coffee-footer-meta">
      데이터 출처: Coffee Quality Institute (CQI) Coffee Quality Database —
      <a class="coffee-footer-link" href="https://github.com/jldbc/coffee-quality-database" target="_blank" rel="noopener noreferrer">
        GitHub (jldbc/coffee-quality-database)
      </a>
    </div>
  </div>
  <div class="coffee-footer-meta">
    CQI 100점 커핑 프로토콜 기준 · 80점 이상 스페셜티 등급
  </div>
</footer>
"""
    _render_html(footer_html)
