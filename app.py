"""월드 스페셜티 커피 아틀라스 (World Specialty Coffee Atlas).

국제 커피 품질 연구소(CQI) 커핑 데이터를 바탕으로 세계 커피 원산지 분포,
인터랙티브 향미 파이차트, 산지별 관능 프로필, 재배 고도와 가공방식의 관계를
소개하는 스페셜티 커피 도감 웹사이트입니다.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import streamlit as st

from charts import (
    MAP_METRIC_OPTIONS,
    PIE_MODE_OPTIONS,
    build_altitude_processing_chart,
    build_flavor_pie_chart,
    build_origin_radar_chart,
    build_top_origins_bar,
    build_world_coffee_map,
)
from data_loader import (
    ARCHETYPE_DESCRIPTIONS_KO,
    SENSORY_COLS,
    SENSORY_DESCRIPTIONS_KO,
    SENSORY_LABELS_KO,
    get_origin_story,
    load_coffee_data,
    summarize_by_archetype,
    summarize_by_country,
    summarize_by_processing,
)
from styles import (
    inject_custom_css,
    render_bean_card,
    render_callout_card,
    render_coffee_guide,
    render_footer,
    render_hero,
    render_kpi_strip,
    render_section_header,
)

DATA_PATH: Path = Path(__file__).parent / "data" / "coffee_quality.csv"

_CONTINENT_ORDER: tuple[str, ...] = (
    "중남미",
    "남미",
    "아프리카",
    "아시아",
    "북미 · 카리브",
    "오세아니아",
)

_PROCESSING_ORDER: tuple[str, ...] = (
    "워시드 (수세식)",
    "내추럴 (건식)",
    "허니 / 펄프드 내추럴",
    "세미워시드",
    "기타 / 미상",
)

_PLOTLY_CONFIG: dict[str, object] = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
}

_ARCHIVE_COLUMN_MAP: dict[str, str] = {
    "country_ko": "원산지",
    "continent_ko": "권역",
    "species": "품종군",
    "variety": "세부 품종",
    "processing_ko": "가공방식",
    "altitude_m": "재배 고도(m)",
    "total_cup_points": "커핑 총점",
    "flavor_archetype": "향미 스타일",
    "flavor_notes_ko": "테이스팅 노트",
    "aroma": "아로마",
    "flavor": "풍미",
    "acidity": "산미",
    "body": "바디감",
    "balance": "밸런스",
}


def _ordered_options(series: pd.Series, preferred: tuple[str, ...]) -> list[str]:
    """Return unique non-empty string values following preferred display ordering."""
    raw = [str(v).strip() for v in series.dropna().unique().tolist() if str(v).strip()]
    unique_set = set(raw)
    ordered = [item for item in preferred if item in unique_set]
    extras = sorted(unique_set - set(ordered))
    return ordered + extras


def _select_curated_beans(view: pd.DataFrame, max_cards: int = 3) -> pd.DataFrame:
    """Select up to max_cards top-scoring beans, preferring distinct origins when available."""
    ranked = view.sort_values(
        by=["total_cup_points", "flavor", "aroma"],
        ascending=[False, False, False],
        na_position="last",
    )
    if len(ranked) <= max_cards:
        return ranked.reset_index(drop=True)

    distinct_origins = ranked.drop_duplicates(subset=["country_ko"], keep="first")
    if len(distinct_origins) >= max_cards:
        return distinct_origins.head(max_cards).reset_index(drop=True)

    chosen_idx = list(distinct_origins.index)
    for idx in ranked.index:
        if idx not in chosen_idx:
            chosen_idx.append(idx)
        if len(chosen_idx) >= max_cards:
            break
    return ranked.loc[chosen_idx].reset_index(drop=True)


def _build_kpi_items(view: pd.DataFrame, total_raw: int) -> list[dict[str, str]]:
    """Compute the 4 live KPI cards for the filtered specialty coffee view."""
    n_beans = len(view)
    n_countries = int(view["country_ko"].nunique())
    n_continents = int(view["continent_ko"].nunique())
    avg_score = float(view["total_cup_points"].mean())

    arabica_cnt = int((view["species"] == "Arabica").sum())
    robusta_cnt = int((view["species"] == "Robusta").sum())
    share_of_all = (n_beans / total_raw * 100.0) if total_raw > 0 else 0.0
    species_sub = f"전체 대비 {share_of_all:.1f}% · 아라비카 {arabica_cnt:,} · 로부스타 {robusta_cnt:,}"

    country_counts = view["country_ko"].value_counts()
    top_vol_country = str(country_counts.index[0]) if not country_counts.empty else "—"
    top_vol_n = int(country_counts.iloc[0]) if not country_counts.empty else 0

    best_idx = view["total_cup_points"].idxmax()
    best_row = view.loc[best_idx]
    best_score = float(best_row["total_cup_points"])
    best_country = str(best_row["country_ko"])
    specialty_pct = float((view["total_cup_points"] >= 80.0).mean() * 100.0)

    arch_df = summarize_by_archetype(view)
    if not arch_df.empty:
        top_arch = str(arch_df.iloc[0]["flavor_archetype"])
        top_arch_share = float(arch_df.iloc[0]["share_pct"])
        top_arch_avg = float(arch_df.iloc[0]["avg_score"])
        arch_sub = f"비중 {top_arch_share:.1f}% · 평균 {top_arch_avg:.2f}점"
    else:
        top_arch = "스페셜티 밸런스"
        arch_sub = "관능 프로파일 요약"

    return [
        {
            "label": "탐색 원두 수",
            "value": f"{n_beans:,}종",
            "sub": species_sub,
        },
        {
            "label": "원산지 국가 수",
            "value": f"{n_countries}개국",
            "sub": f"{n_continents}개 권역 · 최다 등록 {top_vol_country} ({top_vol_n:,}종)",
        },
        {
            "label": "평균 커핑 점수",
            "value": f"{avg_score:.2f}점",
            "sub": f"최고 {best_score:.2f}점 ({best_country}) · 80점+ {specialty_pct:.1f}%",
        },
        {
            "label": "대표 향미 스타일",
            "value": top_arch,
            "sub": arch_sub,
        },
    ]


def main() -> None:
    st.set_page_config(
        page_title="월드 스페셜티 커피 아틀라스 | World Specialty Coffee Atlas",
        page_icon="☕",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()

    df = load_coffee_data()
    if df.empty:
        st.error("불러온 커피 데이터가 비어 있습니다. data/coffee_quality.csv 파일을 확인해 주세요.")
        st.stop()

    species_options = sorted(
        str(v).strip() for v in df["species"].dropna().unique().tolist() if str(v).strip()
    )
    continent_options = _ordered_options(df["continent_ko"], _CONTINENT_ORDER)
    processing_options = _ordered_options(df["processing_ko"], _PROCESSING_ORDER)

    score_series = pd.to_numeric(df["total_cup_points"], errors="coerce").dropna()
    min_score = float(math.floor(float(score_series.min()) * 2.0) / 2.0)
    max_score = float(math.ceil(float(score_series.max()) * 2.0) / 2.0)
    if min_score >= max_score:
        max_score = min_score + 0.5

    # ── Sidebar: Tasting Bar Filter Controls ──────────────────────────────────
    with st.sidebar:
        st.markdown("### ☕ 테이스팅 바 필터")
        st.caption(
            "원산지 권역, 품종, 가공방식과 커핑 점수를 조합해 세계 스페셜티 커피의 테루아를 탐색해 보세요."
        )

        selected_species = st.multiselect(
            "원두 품종군 (Species)",
            options=species_options,
            default=species_options,
            placeholder="품종군을 선택하세요",
        )
        selected_continents = st.multiselect(
            "대륙 / 권역",
            options=continent_options,
            default=continent_options,
            placeholder="권역을 선택하세요",
        )
        selected_processing = st.multiselect(
            "가공 방식",
            options=processing_options,
            default=processing_options,
            placeholder="가공 방식을 선택하세요",
        )
        score_range = st.slider(
            "커핑 총점 범위 (CQI 100점)",
            min_value=min_score,
            max_value=max_score,
            value=(min_score, max_score),
            step=0.5,
            format="%.1f점",
        )

        st.divider()
        st.markdown("#### 차트 보기 설정")
        selected_map_metric_label = st.selectbox(
            "세계 지도 표시 지표",
            options=list(MAP_METRIC_OPTIONS.keys()),
            index=0,
        )
        map_metric_key = MAP_METRIC_OPTIONS[selected_map_metric_label]

        selected_pie_mode_label = st.radio(
            "향미 파이차트 모드",
            options=list(PIE_MODE_OPTIONS.keys()),
            index=0,
        )
        pie_mode_key = PIE_MODE_OPTIONS[selected_pie_mode_label]

        st.divider()
        st.caption(
            "**CQI 스페셜티 등급 기준**\n\n"
            "• 90점 이상: 아웃스탠딩 (Outstanding)\n"
            "• 85~89.99점: 엑설런트 (Excellent)\n"
            "• 80~84.99점: 베리 굿 (Very Good)"
        )

    # ── Apply Filters + Empty Guard ───────────────────────────────────────────
    view = df[
        df["species"].isin(selected_species)
        & df["continent_ko"].isin(selected_continents)
        & df["processing_ko"].isin(selected_processing)
        & (df["total_cup_points"] >= score_range[0])
        & (df["total_cup_points"] <= score_range[1])
    ].copy()

    if view.empty:
        render_hero(0, 0, float("nan"))
        st.warning("선택하신 조건에 해당하는 원두가 없습니다. 왼쪽 사이드바 필터를 조정해 보세요.")
        render_footer()
        st.stop()

    # ── Hero & Dynamic KPI Ribbon ─────────────────────────────────────────────
    render_hero(
        total_beans=len(view),
        total_countries=int(view["country_ko"].nunique()),
        avg_score=float(view["total_cup_points"].mean()),
    )
    render_kpi_strip(_build_kpi_items(view, len(df)))

    # ── Section 1: World Coffee Belt Map & Origin Ranking ─────────────────────
    render_section_header(
        eyebrow="WORLD COFFEE BELT",
        title="세계 원두 분포 지도 & 주요 산지 랭킹",
        subtitle=(
            "적도 기준 남·북위 25도 '커피 벨트'를 따라 분포한 세계 스페셜티 산지의 "
            "샘플 규모, 커핑 점수, 향미 지표, 재배 고도를 인터랙티브 지도로 살펴보세요."
        ),
    )

    world_map_fig = build_world_coffee_map(view, metric=map_metric_key)
    st.plotly_chart(world_map_fig, width="stretch", theme=None, config=_PLOTLY_CONFIG)

    country_summary = summarize_by_country(view, by_iso=False)
    proc_summary = summarize_by_processing(view)

    col_rank, col_belt = st.columns([1.35, 1.0], gap="large")
    with col_rank:
        top_origins_fig = build_top_origins_bar(view, top_n=10)
        st.plotly_chart(top_origins_fig, width="stretch", theme=None, config=_PLOTLY_CONFIG)

    with col_belt:
        if not country_summary.empty:
            top_score_row = country_summary.iloc[0]
            vol_row = country_summary.sort_values(
                by=["sample_count", "avg_score"], ascending=[False, False]
            ).iloc[0]
            belt_body = (
                f"현재 조건에서는 총 {len(country_summary)}개 산지({len(view):,}종)가 커피 벨트 전역에 분포합니다. "
                f"평균 커핑 점수 선두는 {top_score_row['country_ko']}({top_score_row['avg_score']:.2f}점, "
                f"{int(top_score_row['sample_count']):,}종)이며, 가장 많은 샘플이 등록된 산지는 "
                f"{vol_row['country_ko']}({int(vol_row['sample_count']):,}종, 평균 {vol_row['avg_score']:.2f}점)입니다.\n"
                "지도의 점선은 고품질 아라비카와 로부스타가 자라는 적도 남·북위 25° 커피 벨트를 나타냅니다."
            )
        else:
            belt_body = (
                "적도 남·북위 25도 사이의 커피 벨트는 풍부한 일조량과 강수량, 고산지대의 큰 일교차가 어우러져 "
                "스페셜티 커피 재배에 최적의 조건을 제공합니다."
            )
        render_callout_card(
            title="커피 벨트 & 산지 하이라이트",
            body=belt_body,
            badge="ATLAS INSIGHT",
        )

        if not proc_summary.empty:
            lead_proc = proc_summary.iloc[0]
            proc_body = (
                f"선택된 원두 중 가장 비중이 높은 가공방식은 '{lead_proc['processing_ko']}'로 "
                f"전체 {lead_proc['share_pct']:.1f}%({int(lead_proc['count']):,}종)를 차지하며 "
                f"평균 커핑 점수는 {lead_proc['avg_score']:.2f}점입니다. "
                f"(평균 산미 {lead_proc['avg_acidity']:.2f} · 평균 바디감 {lead_proc['avg_body']:.2f})"
            )
            render_callout_card(
                title="가공방식별 프로파일 요약",
                body=proc_body,
                badge="PROCESSING",
            )

    # ── Section 2: Interactive Coffee Flavor Pie Chart & Origin Radar ─────────
    render_section_header(
        eyebrow="FLAVOR PROFILE",
        title="원두 향미 인터랙티브 파이차트 & 산지 관능 비교",
        subtitle=(
            "특정 산지를 선택해 향미 스타일 유형 분포 또는 6대 관능 요소 비율을 파이차트로 확인하고, "
            "여러 원산지의 맛 지문을 레이더 차트 위에서 직접 비교해 보세요."
        ),
    )

    country_by_volume = (
        view["country_ko"].value_counts().index.astype(str).tolist()
    )
    focus_options = ["전체 선택 원두"] + country_by_volume
    default_radar_origins = country_by_volume[: min(4, len(country_by_volume))]

    ctrl_left, ctrl_right = st.columns([1.0, 1.0], gap="large")
    with ctrl_left:
        selected_focus_origin = st.selectbox(
            "향미를 자세히 볼 원산지 선택",
            options=focus_options,
            index=0,
        )
    with ctrl_right:
        selected_radar_origins = st.multiselect(
            "레이더 차트 비교 산지 (최대 4개국)",
            options=country_by_volume,
            default=default_radar_origins,
            max_selections=4,
            placeholder="비교할 산지를 선택하세요 (미선택 시 상위 산지 자동 표시)",
        )

    focus_country_arg = None if selected_focus_origin == "전체 선택 원두" else selected_focus_origin

    if focus_country_arg is not None:
        focus_sub = view[view["country_ko"] == focus_country_arg]
        focus_avg = float(focus_sub["total_cup_points"].mean()) if not focus_sub.empty else float("nan")
        story_text = get_origin_story(focus_country_arg)
        render_callout_card(
            title=f"{focus_country_arg} 테루아 & 향미 스토리 (샘플 {len(focus_sub):,}종 · 평균 {focus_avg:.2f}점)",
            body=story_text,
            badge="ORIGIN STORY",
        )
    else:
        if pie_mode_key == "archetype":
            arch_summary = summarize_by_archetype(view)
            if not arch_summary.empty:
                lead_arch = str(arch_summary.iloc[0]["flavor_archetype"])
                lead_desc = ARCHETYPE_DESCRIPTIONS_KO.get(lead_arch, "")
                render_callout_card(
                    title=f"현재 필터 대표 향미 스타일: {lead_arch} ({arch_summary.iloc[0]['share_pct']:.1f}%)",
                    body=lead_desc,
                    badge="FLAVOR NOTE",
                )
        else:
            sensory_means = {
                col: float(pd.to_numeric(view[col], errors="coerce").mean())
                for col in SENSORY_COLS
                if col in view.columns
            }
            valid_sensory = {k: v for k, v in sensory_means.items() if not math.isnan(v)}
            if valid_sensory:
                top_sensory_key = max(valid_sensory, key=valid_sensory.get)
                top_sensory_label = SENSORY_LABELS_KO.get(top_sensory_key, top_sensory_key)
                render_callout_card(
                    title=f"가장 돋보이는 관능 요소: {top_sensory_label} ({valid_sensory[top_sensory_key]:.2f} / 10)",
                    body=SENSORY_DESCRIPTIONS_KO.get(top_sensory_key, ""),
                    badge="SENSORY PILLAR",
                )

    chart_pie_col, chart_radar_col = st.columns([1.05, 1.0], gap="large")
    with chart_pie_col:
        flavor_pie_fig = build_flavor_pie_chart(
            view,
            mode=pie_mode_key,
            focus_country=focus_country_arg,
        )
        st.plotly_chart(flavor_pie_fig, width="stretch", theme=None, config=_PLOTLY_CONFIG)

    with chart_radar_col:
        radar_fig = build_origin_radar_chart(
            view,
            countries=selected_radar_origins if selected_radar_origins else None,
        )
        st.plotly_chart(radar_fig, width="stretch", theme=None, config=_PLOTLY_CONFIG)

    # ── Section 3: Terroir & Processing + Editorial Coffee Guide ──────────────
    render_section_header(
        eyebrow="TERROIR & PROCESS",
        title="재배 고도와 가공방식이 만드는 커피의 맛",
        subtitle=(
            "고지대일수록 체리가 천천히 익어 복합적인 향미가 응축되며, "
            "워시드·내추럴·허니 가공방식은 한 잔의 산미와 단맛, 바디감의 개성을 결정합니다."
        ),
    )

    altitude_fig = build_altitude_processing_chart(view)
    st.plotly_chart(altitude_fig, width="stretch", theme=None, config=_PLOTLY_CONFIG)

    render_coffee_guide()

    # ── Section 4: Curated Top Specialty Bean Tasting Cards ───────────────────
    render_section_header(
        eyebrow="CURATED BEANS",
        title="스페셜티 원두 큐레이션",
        subtitle=(
            "현재 필터 조건에서 CQI 커핑 총점이 가장 높은 대표 싱글 오리진 원두의 "
            "산지 정보, 테이스팅 노트, 6대 관능 점수를 부티크 로스터리 카드 형식으로 소개합니다."
        ),
    )

    curated_beans = _select_curated_beans(view, max_cards=3)
    card_cols = st.columns(len(curated_beans), gap="medium")
    for col, (_, bean_row) in zip(card_cols, curated_beans.iterrows()):
        with col:
            render_bean_card(bean_row.to_dict())

    # ── Section 5: Tasting Archive Table & CSV Export ─────────────────────────
    render_section_header(
        eyebrow="ARCHIVE",
        title="원두 테이스팅 아카이브 & 데이터 다운로드",
        subtitle=(
            f"필터링된 총 {len(view):,}종의 CQI 커핑 원두 기록을 점수순으로 열람하고 "
            "CSV 파일로 내려받을 수 있습니다."
        ),
    )

    archive_cols = [c for c in _ARCHIVE_COLUMN_MAP if c in view.columns]
    archive_df = (
        view.sort_values(by="total_cup_points", ascending=False)[archive_cols]
        .rename(columns=_ARCHIVE_COLUMN_MAP)
        .reset_index(drop=True)
    )

    st.dataframe(
        archive_df,
        width="stretch",
        height=390,
        hide_index=True,
        column_config={
            "재배 고도(m)": st.column_config.NumberColumn("재배 고도(m)", format="%,.0f m"),
            "커핑 총점": st.column_config.NumberColumn("커핑 총점", format="%.2f점"),
            "아로마": st.column_config.NumberColumn("아로마", format="%.2f"),
            "풍미": st.column_config.NumberColumn("풍미", format="%.2f"),
            "산미": st.column_config.NumberColumn("산미", format="%.2f"),
            "바디감": st.column_config.NumberColumn("바디감", format="%.2f"),
            "밸런스": st.column_config.NumberColumn("밸런스", format="%.2f"),
        },
    )

    csv_bytes = view.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label=f"☕ 필터링된 원두 아카이브 CSV 다운로드 ({len(view):,}종)",
        data=csv_bytes,
        file_name="coffee_quality_filtered.csv",
        mime="text/csv",
    )

    render_footer()


if __name__ == "__main__":
    main()
