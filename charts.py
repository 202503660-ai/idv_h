"""Interactive Plotly visualization builders for the World Specialty Coffee Atlas.

All figures inherit the editorial parchment-and-espresso palette defined in
`styles.py` and aggregate data via pure helpers in `data_loader.py`.
Uses only Python stdlib, pandas, and plotly (no numpy/matplotlib/seaborn).
"""

from __future__ import annotations

import html
import math
from typing import Any

import pandas as pd
import plotly.graph_objects as go

from data_loader import (
    ARCHETYPE_DESCRIPTIONS_KO,
    SENSORY_COLS,
    SENSORY_DESCRIPTIONS_KO,
    SENSORY_LABELS_KO,
    get_flavor_profile,
    summarize_by_archetype,
    summarize_by_country,
)
from styles import COFFEE_PALETTE, PLOTLY_LAYOUT_DEFAULTS

MAP_METRIC_OPTIONS: dict[str, str] = {
    "원두 샘플 수": "sample_count",
    "평균 커핑 점수": "avg_score",
    "평균 아로마": "aroma",
    "평균 산미": "acidity",
    "평균 재배 고도(m)": "avg_altitude_m",
}

PIE_MODE_OPTIONS: dict[str, str] = {
    "향미 스타일 유형 분포": "archetype",
    "향미 6대 요소 비율": "sensory",
}

_MAP_METRIC_META: dict[str, dict[str, str]] = {
    "sample_count": {
        "label": "원두 샘플 수",
        "colorbar_title": "샘플 수 (종)",
        "tickformat": ",d",
        "subtitle": "CQI 등록 샘플 기준",
    },
    "avg_score": {
        "label": "평균 커핑 점수",
        "colorbar_title": "평균 점수 (점)",
        "tickformat": ".1f",
        "subtitle": "100점 만점 커핑 총점",
    },
    "aroma": {
        "label": "평균 아로마",
        "colorbar_title": "아로마 (10점)",
        "tickformat": ".2f",
        "subtitle": "건향·습향 복합성 평가",
    },
    "acidity": {
        "label": "평균 산미",
        "colorbar_title": "산미 (10점)",
        "tickformat": ".2f",
        "subtitle": "생동감·청량감 평가",
    },
    "avg_altitude_m": {
        "label": "평균 재배 고도(m)",
        "colorbar_title": "평균 고도 (m)",
        "tickformat": ",.0f",
        "subtitle": "유효 고도 기록 기준",
    },
}

_SENSORY_EN_LABELS: dict[str, str] = {
    "aroma": "Aroma",
    "flavor": "Flavor",
    "aftertaste": "Aftertaste",
    "acidity": "Acidity",
    "body": "Body",
    "balance": "Balance",
}

_PROCESSING_ORDER: tuple[str, ...] = (
    "워시드 (수세식)",
    "내추럴 (건식)",
    "허니 / 펄프드 내추럴",
    "세미워시드",
    "기타 / 미상",
)

_BAR_COLOR_RAMP: tuple[str, ...] = (
    "#D9B68C",
    "#C68B59",
    "#9A4D22",
    "#6A3519",
    "#3C2415",
)

_RADAR_PALETTE: tuple[str, ...] = (
    COFFEE_PALETTE["primary"],
    COFFEE_PALETTE["sage"],
    COFFEE_PALETTE["berry"],
    COFFEE_PALETTE["espresso"],
)


def _is_finite(value: Any) -> bool:
    """Return True when value can be parsed as a finite float."""
    if value is None or pd.isna(value):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _fmt_num(
    value: Any,
    decimals: int = 2,
    suffix: str = "",
    default: str = "정보 없음",
) -> str:
    """Format a finite numeric value with fixed decimals, or return default."""
    if not _is_finite(value):
        return default
    return f"{float(value):.{decimals}f}{suffix}"


def _fmt_int(value: Any, suffix: str = "", default: str = "정보 없음") -> str:
    """Format a finite numeric value as a comma-separated integer."""
    if not _is_finite(value):
        return default
    return f"{int(round(float(value))):,}{suffix}"


def _clean_text(value: Any, default: str = "정보 없음") -> str:
    """Convert any scalar into an HTML-escaped display string."""
    if value is None or pd.isna(value):
        return html.escape(default, quote=True)
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "n/a"}:
        return html.escape(default, quote=True)
    return html.escape(text, quote=True)


def _wrap_hover_text(text: str, width: int = 30) -> str:
    """Insert <br> line breaks into long tooltip text without cutting words abruptly."""
    cleaned = html.escape(str(text).strip(), quote=True) if text else ""
    if not cleaned or len(cleaned) <= width:
        return cleaned
    words = cleaned.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "<br>".join(lines)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Parse a 6-digit hex color string into an (R, G, B) tuple."""
    code = hex_color.lstrip("#")
    if len(code) != 6:
        return (154, 77, 34)
    return (int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16))


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert a hex color and alpha in [0, 1] into a CSS rgba() string."""
    r, g, b = _hex_to_rgb(hex_color)
    clamped = max(0.0, min(1.0, float(alpha)))
    return f"rgba({r}, {g}, {b}, {clamped:.2f})"


def _interpolate_color(t: float, ramp: tuple[str, ...] = _BAR_COLOR_RAMP) -> str:
    """Interpolate a hex color smoothly along a multi-stop hex ramp."""
    if not ramp:
        return COFFEE_PALETTE["primary"]
    if len(ramp) == 1:
        return ramp[0]
    clamped = max(0.0, min(1.0, float(t)))
    scaled = clamped * (len(ramp) - 1)
    idx = min(int(math.floor(scaled)), len(ramp) - 2)
    frac = scaled - idx
    r1, g1, b1 = _hex_to_rgb(ramp[idx])
    r2, g2, b2 = _hex_to_rgb(ramp[idx + 1])
    r = int(round(r1 + (r2 - r1) * frac))
    g = int(round(g1 + (g2 - g1) * frac))
    b = int(round(b1 + (b2 - b1) * frac))
    return f"#{r:02X}{g:02X}{b:02X}"


def _resolve_archetype_color(archetype: str) -> str:
    """Look up a flavor archetype color from COFFEE_PALETTE with safe fallback."""
    colors: dict[str, str] = COFFEE_PALETTE["archetype_colors"]
    if archetype in colors:
        return colors[archetype]
    if "플로럴" in archetype or "브라이트" in archetype:
        return COFFEE_PALETTE["gold"]
    if "프루티" in archetype or "쥬시" in archetype:
        return COFFEE_PALETTE["berry"]
    if "초콜릿" in archetype or "풀바디" in archetype:
        return COFFEE_PALETTE["espresso"]
    if "스위트" in archetype or "클린" in archetype:
        return COFFEE_PALETTE["sage"]
    return COFFEE_PALETTE["primary"]


def _resolve_processing_color(processing: str) -> str:
    """Look up a processing method color from COFFEE_PALETTE with safe fallback."""
    colors: dict[str, str] = COFFEE_PALETTE["processing_colors"]
    if processing in colors:
        return colors[processing]
    lower = processing.lower()
    if "세미" in processing or "semi" in lower:
        return COFFEE_PALETTE["primary"]
    if "허니" in processing or "펄프드" in processing or "honey" in lower:
        return COFFEE_PALETTE["gold"]
    if "워시드" in processing or "washed" in lower:
        return COFFEE_PALETTE["sage"]
    if "내추럴" in processing or "natural" in lower:
        return COFFEE_PALETTE["berry"]
    return "#8C7A6B"


def _apply_base_layout(fig: go.Figure, **overrides: Any) -> go.Figure:
    """Apply PLOTLY_LAYOUT_DEFAULTS cleanly without mutating shared constants."""
    base: dict[str, Any] = {}
    for key, val in PLOTLY_LAYOUT_DEFAULTS.items():
        if isinstance(val, dict):
            nested = {k: (dict(v) if isinstance(v, dict) else v) for k, v in val.items()}
            base[key] = nested
        elif isinstance(val, list):
            base[key] = list(val)
        else:
            base[key] = val
    fig.update_layout(**base)
    if overrides:
        fig.update_layout(**overrides)
    return fig


def _build_empty_figure(title: str, message: str, height: int = 420) -> go.Figure:
    """Return an editorial empty-state Plotly figure with a centered Korean note."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="center",
        font={"size": 14, "color": COFFEE_PALETTE["muted"]},
        bgcolor=COFFEE_PALETTE["card"],
        bordercolor=COFFEE_PALETTE["border"],
        borderwidth=1,
        borderpad=16,
    )
    _apply_base_layout(
        fig,
        title={"text": title, "x": 0.02, "xanchor": "left"},
        height=height,
        xaxis={"visible": False, "showgrid": False, "zeroline": False},
        yaxis={"visible": False, "showgrid": False, "zeroline": False},
        margin={"l": 24, "r": 24, "t": 54, "b": 24},
    )
    return fig


def _add_coffee_belt_guides(fig: go.Figure) -> None:
    """Add subtle +25 deg and -25 deg Coffee Belt dashed latitude lines and labels."""
    lons = [float(lon) for lon in range(-180, 181, 5)]
    fig.add_trace(
        go.Scattergeo(
            lon=lons + [None] + lons,
            lat=[25.0] * len(lons) + [None] + [-25.0] * len(lons),
            mode="lines",
            line={
                "color": "rgba(154, 77, 34, 0.50)",
                "width": 1.35,
                "dash": "dash",
            },
            hoverinfo="skip",
            showlegend=False,
            name="커피 벨트",
        )
    )
    fig.add_trace(
        go.Scattergeo(
            lon=[-146.0, -146.0],
            lat=[29.0, -29.0],
            mode="text",
            text=["북위 25° · 커피 벨트", "남위 25° · 커피 벨트"],
            textfont={
                "size": 10.5,
                "color": "rgba(154, 77, 34, 0.88)",
                "family": PLOTLY_LAYOUT_DEFAULTS["font"]["family"],
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )


def _apply_coffee_geo_style(fig: go.Figure) -> None:
    """Configure Natural Earth projection with warm editorial parchment styling."""
    fig.update_geos(
        projection_type="natural earth",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#C8B6A2",
        coastlinewidth=0.75,
        showland=True,
        landcolor="#EFE6DA",
        showocean=True,
        oceancolor="#F5EFE6",
        showlakes=True,
        lakecolor="#F5EFE6",
        showcountries=True,
        countrycolor="#DDD0C0",
        countrywidth=0.6,
        lataxis_range=[-56, 74],
        bgcolor="rgba(0,0,0,0)",
    )


def build_world_coffee_map(df: pd.DataFrame, metric: str = "sample_count") -> go.Figure:
    """Build an interactive World Specialty Coffee Choropleth Map with Coffee Belt guides."""
    metric_key = MAP_METRIC_OPTIONS.get(metric, metric)
    if metric_key not in _MAP_METRIC_META:
        metric_key = "sample_count"
    meta = _MAP_METRIC_META[metric_key]
    title_text = f"세계 커피 벨트 아틀라스 · {meta['label']}"

    summary = summarize_by_country(df, by_iso=True)

    fig = go.Figure()
    if summary.empty:
        _add_coffee_belt_guides(fig)
        _apply_coffee_geo_style(fig)
        fig.add_annotation(
            text="현재 필터 조건에 해당하는 커피 산지가 없습니다.<br>필터를 조정해 세계 커피 벨트를 탐색해 보세요.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="center",
            font={"size": 14, "color": COFFEE_PALETTE["muted"]},
            bgcolor="rgba(255,253,249,0.92)",
            bordercolor=COFFEE_PALETTE["border"],
            borderwidth=1,
            borderpad=14,
        )
        _apply_base_layout(
            fig,
            title={"text": title_text, "x": 0.02, "xanchor": "left"},
            height=500,
            margin={"l": 8, "r": 12, "t": 54, "b": 28},
        )
        return fig

    valid = summary[summary[metric_key].notna()].copy()
    if valid.empty:
        _add_coffee_belt_guides(fig)
        _apply_coffee_geo_style(fig)
        fig.add_annotation(
            text=(
                f"선택한 산지에는 '{meta['label']}' 유효 데이터가 없습니다.<br>"
                "다른 지표를 선택하거나 필터 조건을 넓혀 보세요."
            ),
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            align="center",
            font={"size": 14, "color": COFFEE_PALETTE["muted"]},
            bgcolor="rgba(255,253,249,0.92)",
            bordercolor=COFFEE_PALETTE["border"],
            borderwidth=1,
            borderpad=14,
        )
        _apply_base_layout(
            fig,
            title={"text": title_text, "x": 0.02, "xanchor": "left"},
            height=500,
            margin={"l": 8, "r": 12, "t": 54, "b": 28},
        )
        return fig

    hover_texts: list[str] = []
    for _, row in valid.iterrows():
        ko_name = _clean_text(row.get("country_ko"), "미상")
        en_name = _clean_text(row.get("country"), "")
        continent = _clean_text(row.get("continent_ko"), "기타")
        sample_str = _fmt_int(row.get("sample_count"), "종")
        avg_sc = _fmt_num(row.get("avg_score"), 2, "점")
        max_sc = _fmt_num(row.get("max_score"), 2, "점")
        aroma_s = _fmt_num(row.get("aroma"), 2)
        acidity_s = _fmt_num(row.get("acidity"), 2)
        body_s = _fmt_num(row.get("body"), 2)
        alt_s = _fmt_int(row.get("avg_altitude_m"), " m")
        top_proc = _clean_text(row.get("top_processing"), "기타 / 미상")
        top_arch = _clean_text(row.get("top_archetype"), "스페셜티 밸런스")

        en_part = f" <span style='color:{COFFEE_PALETTE['muted']}'>({en_name})</span>" if en_name else ""
        hover_texts.append(
            f"<b style='font-size:14px;color:{COFFEE_PALETTE['ink']}'>{ko_name}</b>{en_part}<br>"
            f"<span style='color:{COFFEE_PALETTE['primary']}'>권역: {continent}</span><br>"
            f"원두 샘플 수: <b>{sample_str}</b><br>"
            f"평균 커핑 점수: <b>{avg_sc}</b> (최고 {max_sc})<br>"
            f"아로마 {aroma_s} · 산미 {acidity_s} · 바디 {body_s}<br>"
            f"평균 재배 고도: <b>{alt_s}</b><br>"
            f"대표 가공방식: {top_proc}<br>"
            f"대표 향미 스타일: {top_arch}"
        )

    z_values = [float(v) for v in valid[metric_key].tolist()]
    z_min = min(z_values)
    z_max = max(z_values)
    if z_min == z_max:
        if metric_key == "sample_count":
            zmin, zmax = 0.0, max(z_max * 1.4, 2.0)
        elif metric_key == "avg_score":
            zmin, zmax = max(60.0, z_min - 2.0), min(100.0, z_max + 2.0)
        elif metric_key in {"aroma", "acidity"}:
            zmin, zmax = max(5.0, z_min - 0.5), min(10.0, z_max + 0.5)
        else:
            zmin, zmax = max(0.0, z_min - 300.0), z_max + 300.0
    else:
        zmin, zmax = z_min, z_max

    fig.add_trace(
        go.Choropleth(
            locations=valid["iso_alpha"].astype(str).tolist(),
            locationmode="ISO-3",
            z=z_values,
            zmin=zmin,
            zmax=zmax,
            colorscale=COFFEE_PALETTE["map_colorscale"],
            marker_line_color="#FAF6F0",
            marker_line_width=0.85,
            hovertext=hover_texts,
            hovertemplate="%{hovertext}<extra></extra>",
            colorbar={
                "title": {
                    "text": meta["colorbar_title"],
                    "font": {"size": 12, "color": COFFEE_PALETTE["ink"]},
                },
                "thickness": 14,
                "len": 0.72,
                "x": 0.99,
                "outlinecolor": COFFEE_PALETTE["border"],
                "outlinewidth": 1,
                "bgcolor": "rgba(255,253,249,0.78)",
                "tickfont": {"size": 11, "color": COFFEE_PALETTE["muted"]},
                "tickformat": meta["tickformat"],
            },
        )
    )

    _add_coffee_belt_guides(fig)
    _apply_coffee_geo_style(fig)

    fig.add_annotation(
        text="점선 구간(북위 25° ~ 남위 25°): 스페셜티 커피 재배의 중심지 '커피 벨트(Coffee Belt)'",
        x=0.01,
        y=0.01,
        xref="paper",
        yref="paper",
        xanchor="left",
        yanchor="bottom",
        showarrow=False,
        font={"size": 11.5, "color": COFFEE_PALETTE["muted"]},
        bgcolor="rgba(250,246,240,0.82)",
        borderpad=4,
    )

    _apply_base_layout(
        fig,
        title={"text": title_text, "x": 0.02, "xanchor": "left"},
        height=505,
        margin={"l": 8, "r": 12, "t": 54, "b": 28},
    )
    return fig


def _filter_focus_country(
    df: pd.DataFrame,
    focus_country: str | None,
) -> tuple[pd.DataFrame, str]:
    """Filter df to focus_country when provided and not an 'all' sentinel."""
    all_sentinels = {"", "전체", "전체 산지", "전체 선택 원두"}
    if df is None or df.empty:
        scope = str(focus_country).strip() if focus_country else "전체 산지"
        if scope in all_sentinels:
            scope = "전체 산지"
        return pd.DataFrame(columns=df.columns if df is not None else []), scope

    if focus_country is None:
        return df, "전체 산지"

    target = str(focus_country).strip()
    if target in all_sentinels:
        return df, "전체 산지"

    if "country_ko" in df.columns:
        matched = df[df["country_ko"] == target]
        if not matched.empty:
            return matched, target

    if target == "미국 (하와이 포함)" and "iso_alpha" in df.columns:
        matched_usa = df[df["iso_alpha"] == "USA"]
        if not matched_usa.empty:
            return matched_usa, target

    if "country" in df.columns:
        matched_en = df[df["country"] == target]
        if not matched_en.empty:
            return matched_en, target

    return df.iloc[0:0].copy(), target


def build_flavor_pie_chart(
    df: pd.DataFrame,
    mode: str = "archetype",
    focus_country: str | None = None,
) -> go.Figure:
    """Build the centerpiece interactive Coffee Flavor Donut/Pie Chart."""
    mode_key = PIE_MODE_OPTIONS.get(mode, mode)
    if mode_key not in {"archetype", "sensory"}:
        mode_key = "archetype"

    sub_df, scope_label = _filter_focus_country(df, focus_country)
    chart_title = (
        f"{scope_label} · 커피 향미 스타일 분포"
        if mode_key == "archetype"
        else f"{scope_label} · 향미 6대 요소 비율"
    )

    if sub_df.empty:
        return _build_empty_figure(
            title=chart_title,
            message=(
                f"'{_clean_text(scope_label, '선택 산지')}' 조건에 해당하는 향미 데이터가 없습니다.<br>"
                "다른 산지를 선택하거나 필터를 조정해 주세요."
            ),
            height=450,
        )

    total_count = int(len(sub_df))
    if "total_cup_points" in sub_df.columns:
        valid_scores = pd.to_numeric(sub_df["total_cup_points"], errors="coerce").dropna()
        overall_avg = float(valid_scores.mean()) if not valid_scores.empty else float("nan")
    else:
        overall_avg = float("nan")

    fig = go.Figure()

    if mode_key == "archetype":
        arch_df = summarize_by_archetype(sub_df)
        if arch_df.empty:
            return _build_empty_figure(
                title=chart_title,
                message="표시할 향미 스타일 데이터가 없습니다.",
                height=450,
            )

        labels = arch_df["flavor_archetype"].astype(str).tolist()
        values = [int(v) for v in arch_df["count"].tolist()]
        colors = [_resolve_archetype_color(lbl) for lbl in labels]
        pulls = [0.055 if idx == 0 and len(labels) > 1 else 0.0 for idx in range(len(labels))]

        hover_texts: list[str] = []
        for _, row in arch_df.iterrows():
            name = _clean_text(row.get("flavor_archetype"), "기타")
            cnt_s = _fmt_int(row.get("count"), "종")
            share_s = _fmt_num(row.get("share_pct"), 1, "%")
            avg_s = _fmt_num(row.get("avg_score"), 2, "점")
            raw_desc = str(row.get("description_ko") or ARCHETYPE_DESCRIPTIONS_KO.get(str(row.get("flavor_archetype")), ""))
            wrapped_desc = _wrap_hover_text(raw_desc, width=28)
            desc_line = (
                f"<br><span style='color:{COFFEE_PALETTE['muted']}'>{wrapped_desc}</span>"
                if wrapped_desc
                else ""
            )
            hover_texts.append(
                f"<b style='font-size:14px;color:{COFFEE_PALETTE['ink']}'>{name}</b><br>"
                f"원두 수: <b>{cnt_s}</b> ({share_s})<br>"
                f"평균 커핑 점수: <b>{avg_s}</b>"
                f"{desc_line}"
            )

        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.48,
                sort=False,
                direction="clockwise",
                pull=pulls,
                marker={
                    "colors": colors,
                    "line": {"color": COFFEE_PALETTE["background"], "width": 2.5},
                },
                textinfo="percent",
                texttemplate="%{percent:.1%}",
                textposition="inside",
                insidetextorientation="horizontal",
                textfont={"size": 12, "color": "#FAF6F0"},
                hovertext=hover_texts,
                hovertemplate="%{hovertext}<extra></extra>",
            )
        )

        center_html = (
            f"<span style='font-size:11px;color:{COFFEE_PALETTE['muted']}'>"
            f"{_clean_text(scope_label, '전체 산지')}</span><br>"
            f"<b style='font-size:21px;color:{COFFEE_PALETTE['ink']}'>{total_count:,}종</b><br>"
            f"<span style='font-size:12px;color:{COFFEE_PALETTE['primary']}'>"
            f"평균 {_fmt_num(overall_avg, 2, '점')}</span>"
        )
    else:
        prof_df = get_flavor_profile(sub_df)
        if prof_df.empty:
            return _build_empty_figure(
                title=chart_title,
                message="표시할 향미 6대 요소 데이터가 없습니다.",
                height=450,
            )

        metrics = prof_df["metric"].astype(str).tolist()
        labels = prof_df["label_ko"].astype(str).tolist()
        values = [float(v) for v in prof_df["mean_score"].tolist()]
        colors = [
            COFFEE_PALETTE["sensory_colors"].get(m, COFFEE_PALETTE["primary"])
            for m in metrics
        ]
        max_val = max(values)
        top_idx = values.index(max_val)
        pulls = [
            0.055 if idx == top_idx and len(values) > 1 else 0.0
            for idx in range(len(values))
        ]
        total_sum = sum(values)

        slice_texts = [f"{lbl}<br>{val:.2f}" for lbl, val in zip(labels, values)]
        hover_texts = []
        for _, row in prof_df.iterrows():
            m_key = str(row.get("metric", ""))
            lbl = _clean_text(row.get("label_ko"), m_key)
            en_lbl = _SENSORY_EN_LABELS.get(m_key, m_key.title())
            mean_val = float(row.get("mean_score", 0.0))
            share_pct = (mean_val / total_sum * 100.0) if total_sum > 0 else 0.0
            min_s = _fmt_num(row.get("min_score"), 2)
            max_s = _fmt_num(row.get("max_score"), 2)
            med_s = _fmt_num(row.get("median_score"), 2)
            desc = _wrap_hover_text(SENSORY_DESCRIPTIONS_KO.get(m_key, ""), width=28)
            desc_line = (
                f"<br><span style='color:{COFFEE_PALETTE['muted']}'>{desc}</span>"
                if desc
                else ""
            )
            hover_texts.append(
                f"<b style='font-size:14px;color:{COFFEE_PALETTE['ink']}'>{lbl}</b> "
                f"<span style='color:{COFFEE_PALETTE['muted']}'>({en_lbl})</span><br>"
                f"평균 점수: <b>{mean_val:.2f} / 10</b><br>"
                f"6대 요소 비중: <b>{share_pct:.1f}%</b><br>"
                f"분포 범위: {min_s} ~ {max_s} (중앙값 {med_s})"
                f"{desc_line}"
            )

        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.48,
                sort=False,
                direction="clockwise",
                pull=pulls,
                marker={
                    "colors": colors,
                    "line": {"color": COFFEE_PALETTE["background"], "width": 2.5},
                },
                text=slice_texts,
                textinfo="text",
                textposition="inside",
                insidetextorientation="horizontal",
                textfont={"size": 11.5, "color": "#FAF6F0"},
                hovertext=hover_texts,
                hovertemplate="%{hovertext}<extra></extra>",
            )
        )

        center_html = (
            f"<span style='font-size:11px;color:{COFFEE_PALETTE['muted']}'>"
            f"{_clean_text(scope_label, '전체 산지')}</span><br>"
            f"<b style='font-size:21px;color:{COFFEE_PALETTE['ink']}'>"
            f"{_fmt_num(overall_avg, 2, '점')}</b><br>"
            f"<span style='font-size:12px;color:{COFFEE_PALETTE['primary']}'>"
            f"평균 총점 · {total_count:,}종</span>"
        )

    fig.add_annotation(
        text=center_html,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="center",
    )

    _apply_base_layout(
        fig,
        title={"text": chart_title, "x": 0.02, "xanchor": "left"},
        height=455,
        uniformtext={"minsize": 9, "mode": "hide"},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.05,
            "xanchor": "center",
            "x": 0.5,
            "itemsizing": "constant",
        },
        margin={"l": 20, "r": 20, "t": 56, "b": 88},
    )
    return fig


def build_origin_radar_chart(
    df: pd.DataFrame,
    countries: list[str] | None = None,
) -> go.Figure:
    """Build an interactive Polar Radar Chart comparing up to 4 origins across 6 sensory pillars."""
    chart_title = "산지별 6대 향미 프로파일 비교"
    if df is None or df.empty or "country_ko" not in df.columns:
        return _build_empty_figure(
            title=chart_title,
            message="비교할 커피 산지 데이터가 없습니다.<br>사이드바 필터를 조정해 주세요.",
            height=460,
        )

    country_summary = summarize_by_country(df, by_iso=False)
    if country_summary.empty:
        return _build_empty_figure(
            title=chart_title,
            message="비교할 커피 산지 데이터가 없습니다.<br>사이드바 필터를 조정해 주세요.",
            height=460,
        )

    available_set = set(country_summary["country_ko"].astype(str).tolist())
    chosen: list[str] = []

    if countries:
        seen: set[str] = set()
        for raw_name in countries:
            name = str(raw_name).strip()
            if not name or name == "전체" or name in seen:
                continue
            if name in available_set or (
                name == "미국 (하와이 포함)"
                and "iso_alpha" in df.columns
                and (df["iso_alpha"] == "USA").any()
            ):
                seen.add(name)
                chosen.append(name)
            if len(chosen) >= 4:
                break
        if not chosen:
            return _build_empty_figure(
                title=chart_title,
                message="선택한 산지가 현재 필터 결과에 없습니다.<br>다른 산지를 선택하거나 필터를 해제해 주세요.",
                height=460,
            )
    else:
        ranked = country_summary.sort_values(
            by=["sample_count", "avg_score", "country_ko"],
            ascending=[False, False, True],
        )
        chosen = ranked["country_ko"].astype(str).head(4).tolist()

    fig = go.Figure()
    all_vals: list[float] = []
    fill_alpha = 0.22 if len(chosen) == 1 else 0.16

    for idx, origin_name in enumerate(chosen):
        if origin_name in available_set:
            sub = df[df["country_ko"] == origin_name]
        else:
            sub = df[df["iso_alpha"] == "USA"]

        prof = get_flavor_profile(sub)
        if prof.empty:
            continue

        metric_map = {
            str(row["metric"]): float(row["mean_score"])
            for _, row in prof.iterrows()
            if _is_finite(row.get("mean_score"))
        }
        ordered_cols = [col for col in SENSORY_COLS if col in metric_map]
        if not ordered_cols:
            continue

        labels = [SENSORY_LABELS_KO.get(col, col) for col in ordered_cols]
        vals = [metric_map[col] for col in ordered_cols]
        all_vals.extend(vals)

        avg_total = float("nan")
        if "total_cup_points" in sub.columns:
            sc_series = pd.to_numeric(sub["total_cup_points"], errors="coerce").dropna()
            if not sc_series.empty:
                avg_total = float(sc_series.mean())

        color = _RADAR_PALETTE[idx % len(_RADAR_PALETTE)]
        closed_theta = labels + [labels[0]]
        closed_r = vals + [vals[0]]

        safe_origin = _clean_text(origin_name, "산지")
        avg_total_str = _fmt_num(avg_total, 2, "점")
        sample_cnt = int(len(sub))
        hover_texts = [
            (
                f"<b style='font-size:14px;color:{COFFEE_PALETTE['ink']}'>{safe_origin}</b> "
                f"<span style='color:{COFFEE_PALETTE['muted']}'>(n={sample_cnt:,}종)</span><br>"
                f"{lbl}: <b>{val:.2f} / 10</b><br>"
                f"평균 커핑 총점: <b>{avg_total_str}</b>"
            )
            for lbl, val in zip(closed_theta, closed_r)
        ]

        fig.add_trace(
            go.Scatterpolar(
                r=closed_r,
                theta=closed_theta,
                fill="toself",
                fillcolor=_rgba(color, fill_alpha),
                name=f"{origin_name} (n={sample_cnt:,})",
                mode="lines+markers",
                line={"color": color, "width": 2.4},
                marker={
                    "size": 6.5,
                    "color": color,
                    "line": {"color": COFFEE_PALETTE["background"], "width": 1.2},
                },
                hovertext=hover_texts,
                hovertemplate="%{hovertext}<extra></extra>",
            )
        )

    if not all_vals:
        return _build_empty_figure(
            title=chart_title,
            message="선택한 산지의 향미 점수 데이터가 충분하지 않습니다.",
            height=460,
        )

    min_val = min(all_vals)
    max_val = max(all_vals)
    floor_base = 5.0 if min_val >= 5.2 else 0.0
    r_min = round(max(floor_base, min_val - 0.5), 2)
    r_max = round(min(10.0, max_val + 0.3), 2)
    if r_max - r_min < 0.6:
        r_min = round(max(0.0, r_max - 0.6), 2)

    _apply_base_layout(
        fig,
        title={"text": chart_title, "x": 0.02, "xanchor": "left"},
        height=465,
        polar={
            "bgcolor": "rgba(255, 253, 249, 0.74)",
            "radialaxis": {
                "visible": True,
                "range": [r_min, r_max],
                "nticks": 5,
                "gridcolor": COFFEE_PALETTE["border"],
                "linecolor": COFFEE_PALETTE["border"],
                "tickfont": {"size": 10.5, "color": COFFEE_PALETTE["muted"]},
            },
            "angularaxis": {
                "direction": "clockwise",
                "rotation": 90,
                "gridcolor": COFFEE_PALETTE["border"],
                "linecolor": COFFEE_PALETTE["border"],
                "tickfont": {"size": 12.5, "color": COFFEE_PALETTE["ink"]},
            },
        },
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.09,
            "xanchor": "center",
            "x": 0.5,
        },
        margin={"l": 48, "r": 48, "t": 56, "b": 88},
    )
    return fig


def build_altitude_processing_chart(df: pd.DataFrame) -> go.Figure:
    """Build an interactive Altitude vs. Cupping Score scatter chart colored by processing."""
    chart_title = "재배 고도·가공방식별 커핑 점수 분포"
    if df is None or df.empty:
        return _build_empty_figure(
            title=chart_title,
            message="표시할 커피 원두 데이터가 없습니다.<br>사이드바 필터를 조정해 주세요.",
            height=450,
        )

    if "altitude_m" not in df.columns or "total_cup_points" not in df.columns:
        return _build_empty_figure(
            title=chart_title,
            message="고도 또는 커핑 점수 컬럼이 없어 산점도를 그릴 수 없습니다.",
            height=450,
        )

    work = df.copy()
    work["_alt_num"] = pd.to_numeric(work["altitude_m"], errors="coerce")
    work["_score_num"] = pd.to_numeric(work["total_cup_points"], errors="coerce")
    valid = work[work["_alt_num"].notna() & work["_score_num"].notna()].copy()

    if valid.empty:
        return _build_empty_figure(
            title=chart_title,
            message=(
                "현재 필터 조건에 유효한 재배 고도(m) 데이터가 없습니다.<br>"
                "다른 산지나 필터 조건을 선택해 고도와 커핑 점수의 관계를 확인해 보세요."
            ),
            height=450,
        )

    if "processing_ko" in valid.columns:
        proc_series = valid["processing_ko"].fillna("기타 / 미상").astype(str).str.strip()
        proc_series = proc_series.replace("", "기타 / 미상")
    else:
        proc_series = pd.Series(["기타 / 미상"] * len(valid), index=valid.index)
    valid["_proc_label"] = proc_series

    existing_procs = valid["_proc_label"].unique().tolist()
    ordered_procs = [p for p in _PROCESSING_ORDER if p in existing_procs]
    ordered_procs.extend(sorted(p for p in existing_procs if p not in ordered_procs))

    marker_size = 10 if len(valid) <= 25 else 8.5
    marker_opacity = 0.88 if len(valid) <= 25 else 0.76

    fig = go.Figure()
    for proc in ordered_procs:
        grp = valid[valid["_proc_label"] == proc]
        color = _resolve_processing_color(proc)

        hover_texts: list[str] = []
        for _, row in grp.iterrows():
            country_s = _clean_text(row.get("country_ko") or row.get("country"), "미상")
            region_raw = str(row.get("region", "")).strip()
            farm_raw = str(row.get("farm_name", "")).strip()
            place_parts = [
                _clean_text(part, "")
                for part in (region_raw, farm_raw)
                if part and part.lower() not in {"nan", "none", "null"}
            ]
            place_s = " · ".join(place_parts) if place_parts else "상세 지역 정보 없음"
            variety_s = _clean_text(row.get("variety"), "미상")
            proc_s = _clean_text(proc, "기타 / 미상")
            alt_s = _fmt_int(row.get("_alt_num"), " m")
            score_s = _fmt_num(row.get("_score_num"), 2, "점")
            arch_s = _clean_text(row.get("flavor_archetype"), "스페셜티 밸런스")
            notes_raw = str(row.get("flavor_notes_ko", "")).strip()
            notes_s = _wrap_hover_text(notes_raw, width=28) if notes_raw else "테이스팅 노트 정보 없음"

            hover_texts.append(
                f"<b style='font-size:14px;color:{COFFEE_PALETTE['ink']}'>{country_s}</b><br>"
                f"<span style='color:{COFFEE_PALETTE['muted']}'>{place_s}</span><br>"
                f"품종: {variety_s} · 가공: <b>{proc_s}</b><br>"
                f"재배 고도: <b>{alt_s}</b> · 커핑 총점: <b>{score_s}</b><br>"
                f"향미 스타일: {arch_s}<br>"
                f"<span style='color:{COFFEE_PALETTE['primary']}'>노트: {notes_s}</span>"
            )

        fig.add_trace(
            go.Scatter(
                x=grp["_alt_num"].tolist(),
                y=grp["_score_num"].tolist(),
                mode="markers",
                name=f"{proc} ({len(grp):,})",
                marker={
                    "color": color,
                    "size": marker_size,
                    "opacity": marker_opacity,
                    "line": {"width": 0.9, "color": COFFEE_PALETTE["background"]},
                },
                hovertext=hover_texts,
                hovertemplate="%{hovertext}<extra></extra>",
            )
        )

    x_min = float(valid["_alt_num"].min())
    x_max = float(valid["_alt_num"].max())
    y_min = float(valid["_score_num"].min())
    y_max = float(valid["_score_num"].max())

    if x_min == x_max:
        x_range = [max(0.0, x_min - 250.0), x_max + 250.0]
    else:
        x_pad = max(60.0, (x_max - x_min) * 0.06)
        x_range = [max(0.0, x_min - x_pad), x_max + x_pad]

    if y_min == y_max:
        y_range = [max(50.0, y_min - 2.0), min(100.0, y_max + 2.0)]
    else:
        y_pad = max(0.6, (y_max - y_min) * 0.08)
        y_range = [max(50.0, y_min - y_pad), min(100.0, y_max + y_pad)]

    if x_range[0] < 1200.0 < x_range[1]:
        fig.add_vline(
            x=1200.0,
            line_width=1.2,
            line_dash="dot",
            line_color="rgba(154, 77, 34, 0.45)",
            annotation_text="고지대 스페셜티 (1,200m+)",
            annotation_position="top right",
            annotation_font={"size": 11, "color": COFFEE_PALETTE["muted"]},
        )

    if y_range[0] < 80.0 < y_range[1]:
        fig.add_hline(
            y=80.0,
            line_width=1.2,
            line_dash="dot",
            line_color="rgba(78, 110, 88, 0.55)",
            annotation_text="스페셜티 기준 (80점)",
            annotation_position="bottom right",
            annotation_font={"size": 11, "color": COFFEE_PALETTE["sage"]},
        )

    _apply_base_layout(
        fig,
        title={"text": chart_title, "x": 0.02, "xanchor": "left"},
        height=475,
        xaxis={
            "title": {"text": "재배 고도 (m)", "font": {"size": 13, "color": COFFEE_PALETTE["ink"]}},
            "range": x_range,
            "tickformat": ",.0f",
            "gridcolor": "rgba(230, 218, 203, 0.78)",
            "zeroline": False,
            "tickfont": {"size": 11.5, "color": COFFEE_PALETTE["muted"]},
        },
        yaxis={
            "title": {"text": "커핑 총점 (100점 만점)", "font": {"size": 13, "color": COFFEE_PALETTE["ink"]}},
            "range": y_range,
            "gridcolor": "rgba(230, 218, 203, 0.78)",
            "zeroline": False,
            "tickfont": {"size": 11.5, "color": COFFEE_PALETTE["muted"]},
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0.0,
            "title": {"text": "가공방식  ", "font": {"size": 12, "color": COFFEE_PALETTE["muted"]}},
        },
        margin={"l": 60, "r": 24, "t": 90, "b": 56},
    )
    return fig


def build_top_origins_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Build a horizontal bar chart ranking Top N coffee origins by average cup score."""
    chart_title = "평균 커핑 점수 상위 스페셜티 산지"
    summary = summarize_by_country(df, by_iso=False)
    if summary.empty:
        return _build_empty_figure(
            title=chart_title,
            message="표시할 산지 순위 데이터가 없습니다.<br>사이드바 필터를 조정해 주세요.",
            height=380,
        )

    valid = summary[summary["avg_score"].notna()].copy()
    if valid.empty:
        return _build_empty_figure(
            title=chart_title,
            message="유효한 커핑 점수 데이터가 없어 순위를 계산할 수 없습니다.",
            height=380,
        )

    n_limit = max(1, int(top_n))
    ranked = (
        valid.sort_values(
            by=["avg_score", "sample_count", "country_ko"],
            ascending=[False, False, True],
        )
        .head(n_limit)
        .reset_index(drop=True)
    )
    ranked["_rank"] = list(range(1, len(ranked) + 1))

    plot_df = ranked.iloc[::-1].reset_index(drop=True)

    scores = [float(v) for v in plot_df["avg_score"].tolist()]
    min_sc = min(scores)
    max_sc = max(scores)
    if max_sc == min_sc:
        bar_colors = [_interpolate_color(0.72) for _ in scores]
    else:
        bar_colors = [
            _interpolate_color((sc - min_sc) / (max_sc - min_sc))
            for sc in scores
        ]

    bar_labels: list[str] = []
    hover_texts: list[str] = []
    for _, row in plot_df.iterrows():
        rank_num = int(row["_rank"])
        ko_name = _clean_text(row.get("country_ko"), "미상")
        en_name = _clean_text(row.get("country"), "")
        continent = _clean_text(row.get("continent_ko"), "기타")
        avg_sc = float(row["avg_score"])
        max_sc_s = _fmt_num(row.get("max_score"), 2, "점")
        cnt = int(row.get("sample_count", 0))
        aroma_s = _fmt_num(row.get("aroma"), 2)
        acidity_s = _fmt_num(row.get("acidity"), 2)
        body_s = _fmt_num(row.get("body"), 2)
        alt_s = _fmt_int(row.get("avg_altitude_m"), " m")
        top_proc = _clean_text(row.get("top_processing"), "기타 / 미상")
        top_arch = _clean_text(row.get("top_archetype"), "스페셜티 밸런스")

        bar_labels.append(f" {avg_sc:.2f}점 (n={cnt:,})")
        en_part = f" <span style='color:{COFFEE_PALETTE['muted']}'>({en_name})</span>" if en_name else ""
        hover_texts.append(
            f"<b style='font-size:14px;color:{COFFEE_PALETTE['ink']}'>#{rank_num} {ko_name}</b>{en_part}<br>"
            f"<span style='color:{COFFEE_PALETTE['primary']}'>권역: {continent}</span><br>"
            f"평균 커핑 점수: <b>{avg_sc:.2f}점</b> (최고 {max_sc_s})<br>"
            f"원두 샘플 수: <b>{cnt:,}종</b><br>"
            f"아로마 {aroma_s} · 산미 {acidity_s} · 바디 {body_s}<br>"
            f"평균 재배 고도: {alt_s}<br>"
            f"대표 가공방식: {top_proc}<br>"
            f"대표 향미 스타일: {top_arch}"
        )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=scores,
            y=plot_df["country_ko"].astype(str).tolist(),
            orientation="h",
            marker={
                "color": bar_colors,
                "line": {"color": COFFEE_PALETTE["background"], "width": 0.8},
            },
            text=bar_labels,
            textposition="outside",
            cliponaxis=False,
            textfont={"size": 11.5, "color": COFFEE_PALETTE["ink"]},
            hovertext=hover_texts,
            hovertemplate="%{hovertext}<extra></extra>",
            showlegend=False,
        )
    )

    x_min = max(0.0, float(math.floor(min_sc - 4.0)))
    if max_sc - x_min < 4.0:
        x_min = max(0.0, float(math.floor(max_sc - 4.0)))
    x_span = max(4.0, max_sc - x_min)
    x_max = min(104.0, max_sc + max(2.2, x_span * 0.36))

    fig_height = max(320, 118 + len(plot_df) * 34)
    dynamic_title = f"평균 커핑 점수 상위 {len(plot_df)}개 산지"

    _apply_base_layout(
        fig,
        title={"text": dynamic_title, "x": 0.02, "xanchor": "left"},
        height=fig_height,
        bargap=0.28,
        xaxis={
            "title": {"text": "평균 커핑 총점 (점)", "font": {"size": 13, "color": COFFEE_PALETTE["ink"]}},
            "range": [x_min, x_max],
            "gridcolor": "rgba(230, 218, 203, 0.78)",
            "zeroline": False,
            "tickfont": {"size": 11.5, "color": COFFEE_PALETTE["muted"]},
        },
        yaxis={
            "title": None,
            "automargin": True,
            "tickfont": {"size": 12.5, "color": COFFEE_PALETTE["ink"]},
            "showgrid": False,
        },
        margin={"l": 124, "r": 36, "t": 54, "b": 48},
    )
    return fig
