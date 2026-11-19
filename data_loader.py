"""Data loading, metadata constants, and pure aggregation helpers for the Specialty Coffee Atlas."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH: Path = Path(__file__).parent / "data" / "coffee_quality.csv"

SENSORY_COLS: list[str] = [
    "aroma",
    "flavor",
    "aftertaste",
    "acidity",
    "body",
    "balance",
]

SENSORY_LABELS_KO: dict[str, str] = {
    "aroma": "아로마",
    "flavor": "풍미",
    "aftertaste": "여운",
    "acidity": "산미",
    "body": "바디감",
    "balance": "밸런스",
}

SENSORY_DESCRIPTIONS_KO: dict[str, str] = {
    "aroma": "분쇄 직후의 건향(Fragrance)과 추출 시 피어오르는 습향(Aroma)의 복합성과 강도입니다.",
    "flavor": "입안에서 느껴지는 커피 고유의 향미 표현력과 테루아 캐릭터의 선명함을 평가합니다.",
    "aftertaste": "커피를 삼킨 뒤 입안에 남는 긍정적인 향미의 지속 시간과 깔끔한 마무리입니다.",
    "acidity": "신맛이 아닌 과일 같은 생동감과 밝은 청량감(Brightness)을 나타내는 핵심 지표입니다.",
    "body": "혀끝에서 느껴지는 무게감, 점도, 실키하거나 크리미한 질감(Mouthfeel)을 뜻합니다.",
    "balance": "풍미·여운·산미·바디가 어느 한쪽에 치우치지 않고 조화롭게 어우러지는 완성도입니다.",
}

ARCHETYPE_DESCRIPTIONS_KO: dict[str, str] = {
    "플로럴 · 브라이트": "화사한 꽃향기와 시트러스 계열의 밝은 산미가 돋보이는 우아하고 투명한 프로파일입니다.",
    "프루티 · 쥬시": "잘 익은 베리와 핵과류의 과즙미, 생동감 있는 산미와 긴 여운이 매력적인 프로파일입니다.",
    "초콜릿 · 풀바디": "다크초콜릿·구운 견과류의 고소함과 묵직하고 시럽 같은 바디감을 갖춘 클래식 프로파일입니다.",
    "스위트 · 클린컵": "잡미 없는 깔끔한 클린컵 위에 캐러멜·꿀·사탕수수 같은 부드러운 단맛이 돋보이는 프로파일입니다.",
    "스페셜티 밸런스": "아로마·산미·단맛·바디가 정교하게 균형을 이루어 누구나 편안하게 즐기는 완성형 프로파일입니다.",
}

ORIGIN_STORIES_KO: dict[str, str] = {
    "에티오피아": "아라비카 커피의 발상지이자 스페셜티의 성지입니다. 예가체프·시다모·구지 등 해발 1,800~2,200m 고지대에서 자란 재래종(Heirloom)은 자스민 꽃향과 베르가못, 잘 익은 베리의 화사한 향미로 세계 커퍼들의 찬사를 받습니다.",
    "콜롬비아": "안데스 산맥의 세 줄기(코르디예라)가 만들어내는 다채로운 미세기후 덕분에 일 년 내내 신선한 수확이 이어집니다. 워시드 가공을 중심으로 밀크초콜릿, 캐러멜, 잘 익은 붉은 사과의 정교한 밸런스를 보여줍니다.",
    "과테말라": "안티구아·우에우에테낭고 등 화산성 토양과 큰 일교차가 길러낸 복합적인 풍미가 특징입니다. 다크코코아와 구운 아몬드의 묵직한 단맛 위로 오렌지 필과 은은한 스파이스가 어우러집니다.",
    "브라질": "세계 최대 커피 생산국으로, 미나스제라이스와 세하두 지역의 광활한 고원에서 내추럴·펄프드 내추럴 가공이 발달했습니다. 낮은 산미와 헤이즐넛·밀크초콜릿의 고소한 단맛으로 에스프레소 블렌드의 든든한 중심을 이룹니다.",
    "멕시코": "치아파스·베라크루즈·오아하카의 비옥한 산악 지대에서 소농 중심으로 유기농·쉐이드그로운 커피를 재배합니다. 가볍고 깔끔한 바디에 밀크초콜릿, 시나몬, 구운 견과의 부드러운 여운이 인상적입니다.",
    "케냐": "적도 인근 케냐산 기슭의 붉은 화산토와 SL28·SL34 품종, 특유의 더블 워시드 공법이 만나 폭발적인 과실미를 완성합니다. 블랙커런트, 자몽, 와이니한 산미와 쥬시한 텍스처로 독보적인 개성을 자랑합니다.",
    "코스타리카": "타라수·센트럴밸리 등 정교한 마이크로밀(Micro-mill) 문화와 허니 프로세싱의 선구자입니다. 투명한 클린컵에 꿀 같은 단맛, 시트러스와 잘 익은 핵과류의 화사함이 매끄럽게 이어집니다.",
    "온두라스": "중앙아메리카 최대 생산국 중 하나로, 마르칼라·코판 등 고산 지대의 스페셜티 품질이 빠르게 도약했습니다. 토피와 브라운슈거의 달콤함, 잘 익은 자두와 은은한 초콜릿 노트가 돋보입니다.",
    "미국 (하와이)": "빅아일랜드 코나(Kona) 지역의 화산 사면과 해양성 기후, 오후의 구름 그늘이 빚어낸 희소 스페셜티입니다. 마카다미아 너트, 브라운슈거, 실키하고 부드러운 과실 산미로 사랑받습니다.",
    "미국": "하와이와 본토 인증 로트를 포함한 미국 스페셜티 커핑 기록으로, 정교한 품질 관리와 깔끔한 캐러멜·견과류·밀크초콜릿 프로파일이 특징입니다.",
    "대만": "아리산(Alishan)·구컹 등 해발 고도가 높은 아열대 산악 지대에서 소량 생산되는 하이엔드 부티크 커피입니다. 우롱차를 연상시키는 향긋한 꽃향과 사탕수수 같은 맑은 단맛, 뛰어난 클린컵이 매력입니다.",
    "탄자니아": "킬리만자로와 음베야 고지대의 화산토에서 재배되며 피베리(Peaberry)로도 유명합니다. 블랙베리와 감귤류의 선명한 산미, 흑설탕 같은 묵직한 단맛이 균형을 이룹니다.",
    "우간다": "르웬조리 산맥과 엘곤산의 아라비카부터 빅토리아호 인근의 파인 로부스타까지 두 품종이 공존하는 동아프리카 핵심 산지입니다. 다크초콜릿, 말린 과일, 진한 바디감이 돋보입니다.",
    "인도네시아": "수마트라·자바·술라웨시 등 열대 화산섬의 습식 탈곡(Giling Basah) 가공이 독창적인 캐릭터를 만듭니다. 낮은 산미와 묵직한 시럽 바디, 허브·스파이스·다크초콜릿의 깊은 여운이 특징입니다.",
    "태국": "치앙마이·치앙라이 등 북부 고산 지대에서 고품질 아라비카 스페셜티가 빠르게 성장하고 있습니다. 흑설탕과 구운 견과의 편안한 단맛에 은은한 열대과실 뉘앙스가 어우러집니다.",
    "엘살바도르": "파카마라(Pacamara)와 버번 품종의 본고장으로, 화산 사면의 비옥한 토양에서 자란 원두가 유명합니다. 바닐라, 구운 아몬드, 청사과의 부드럽고 크리미한 밸런스를 선사합니다.",
    "니카라과": "히노테가와 마타갈파의 울창한 산림 그늘 아래에서 재배되어 섬세하고 균형 잡힌 컵을 만듭니다. 코코아, 배, 부드러운 견과류와 깔끔한 애프터테이스트가 돋보입니다.",
    "파나마": "보케테(Boquete)와 바루 화산 지대의 미세기후가 세계 최고가 품종인 게이샤(Gesha)의 신화를 썼습니다. 자스민, 복숭아, 홍차 같은 실키하고 우아한 향미가 정점을 이룹니다.",
    "중국": "윈난성 푸얼·바오산 고원 지대를 중심으로 현대적 스페셜티 가공 기술이 빠르게 정착하고 있습니다. 홍차, 말린 자두, 캐러멜의 부드럽고 정돈된 단맛이 매력적입니다.",
    "인도": "카르나타카 치크마갈루르의 울창한 향신료 숲 그늘 아래에서 아라비카와 파인 로부스타를 함께 재배합니다. 다크카카오, 정향·스파이스, 풍부한 크레마와 묵직한 바디가 인상적입니다.",
    "페루": "안데스 동쪽 고산지대의 청정 환경에서 유기농 스페셜티를 주로 생산합니다. 밀크초콜릿과 호두의 고소함에 부드러운 시트러스 산미가 더해져 데일리 커피로 탁월합니다.",
    "말라위": "동아프리카 남부의 고원에서 게이샤와 아가로를 소량 재배하는 숨은 보석 같은 산지입니다. 감귤류와 베리의 산뜻한 산미, 꿀 같은 단맛이 조화롭습니다.",
    "베트남": "중부 고원 달랏과 닥락을 중심으로 세계 2위 커피 생산국 위상을 지니며, 최근 파인 로부스타와 고지대 아라비카가 주목받고 있습니다. 진한 다크초콜릿과 캐러멜, 묵직한 구조감이 특징입니다.",
    "미얀마": "샨주(Shan State) 고원 지대에서 내추럴·워시드 스페셜티로 국제적인 호평을 얻고 있는 신흥 산지입니다. 열대과실과 꿀의 달콤함, 부드러운 카카오 여운을 보여줍니다.",
    "아이티": "카리브해 산악 지대의 전통 타이피카 계열 커피로, 부드러운 코코아와 브라운슈거, 온화한 스파이스의 클래식한 풍미를 지닙니다.",
    "푸에르토리코": "야우코(Yauco) 산악 지대에서 생산되는 역사 깊은 카리브 스페셜티입니다. 진한 카카오와 바닐라, 크리미한 견과류 질감의 우아한 바디감을 선보입니다.",
    "에콰도르": "적도가 지나는 안데스 고산 지대와 갈라파고스 인근의 독특한 테루아에서 자라 플로럴 노트와 열대과실, 사탕수수의 맑은 단맛을 냅니다.",
    "르완다": "천 개의 언덕이라 불리는 고지대 화산토에서 버번 품종을 워시드 가공해 홍차, 크랜베리, 오렌지 블라썸의 세련된 산미를 구현합니다.",
    "부룬디": "고도 1,700m 이상의 비옥한 언덕에서 소농들이 정성껏 수확한 버번 커피로, 히비스커스와 붉은 베리, 사탕수수의 생기 넘치는 단맛이 특징입니다.",
    "코트디부아르": "서아프리카 커피 벨트의 전통 산지로, 묵직한 바디와 구운 카카오·스파이스의 강렬한 캐릭터를 보여줍니다.",
}

_ENGLISH_TO_KO_COUNTRY: dict[str, str] = {
    "Brazil": "브라질",
    "Burundi": "부룬디",
    "China": "중국",
    "Colombia": "콜롬비아",
    "Costa Rica": "코스타리카",
    "Cote d'Ivoire": "코트디부아르",
    "Ecuador": "에콰도르",
    "El Salvador": "엘살바도르",
    "Ethiopia": "에티오피아",
    "Guatemala": "과테말라",
    "Haiti": "아이티",
    "Honduras": "온두라스",
    "India": "인도",
    "Indonesia": "인도네시아",
    "Japan": "일본",
    "Kenya": "케냐",
    "Laos": "라오스",
    "Malawi": "말라위",
    "Mauritius": "모리셔스",
    "Mexico": "멕시코",
    "Myanmar": "미얀마",
    "Nicaragua": "니카라과",
    "Panama": "파나마",
    "Papua New Guinea": "파푸아뉴기니",
    "Peru": "페루",
    "Philippines": "필리핀",
    "Puerto Rico": "푸에르토리코",
    "Rwanda": "르완다",
    "Taiwan": "대만",
    "Tanzania": "탄자니아",
    "Thailand": "태국",
    "Uganda": "우간다",
    "United States": "미국",
    "United States (Hawaii)": "미국 (하와이)",
    "Vietnam": "베트남",
    "Zambia": "잠비아",
}

_TEXT_COLS: tuple[str, ...] = (
    "species",
    "country",
    "country_ko",
    "iso_alpha",
    "continent_ko",
    "region",
    "farm_name",
    "producer",
    "variety",
    "processing_method",
    "processing_ko",
    "color",
    "flavor_archetype",
    "flavor_notes_ko",
)

_NUMERIC_COLS: tuple[str, ...] = (
    "altitude_m",
    "aroma",
    "flavor",
    "aftertaste",
    "acidity",
    "body",
    "balance",
    "uniformity",
    "clean_cup",
    "sweetness",
    "cupper_points",
    "total_cup_points",
    "moisture",
)


@st.cache_data
def load_coffee_data() -> pd.DataFrame:
    """Load the cleaned CQI coffee quality dataset with safe dtypes and graceful error handling."""
    if not DATA_PATH.exists():
        st.error(
            f"데이터 파일을 찾을 수 없습니다: `{DATA_PATH.name}` "
            "(앱 폴더의 `data/coffee_quality.csv` 파일이 함께 포함되었는지 확인해 주세요.)"
        )
        st.stop()

    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8")
    except Exception as exc:
        st.error(f"커피 데이터셋을 읽는 중 오류가 발생했습니다: {exc}")
        st.stop()

    for col in _TEXT_COLS:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)

    for col in _NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "harvest_year" in df.columns:
        df["harvest_year"] = pd.to_numeric(df["harvest_year"], errors="coerce").astype("Int64")

    return df


def _safe_mode(series: pd.Series, default: str = "미상") -> str:
    cleaned = series.dropna()
    cleaned = cleaned[cleaned.astype(str).str.strip() != ""]
    if cleaned.empty:
        return default
    modes = cleaned.mode()
    return str(modes.iloc[0]) if not modes.empty else default


def _safe_mean(series: pd.Series) -> float:
    valid = pd.to_numeric(series, errors="coerce").dropna()
    if valid.empty:
        return float("nan")
    return float(valid.mean())


def summarize_by_country(df: pd.DataFrame, by_iso: bool = True) -> pd.DataFrame:
    """Aggregate coffee scores, sample counts, altitude, and sensory means by origin.

    When `by_iso=True` (default), rolls up records sharing the same ISO-3 code
    (e.g., United States and United States (Hawaii) -> USA) so Plotly world
    choropleth maps never overwrite duplicate ISO locations.
    Handles empty or 1-row DataFrames safely without raising exceptions.
    """
    out_cols = [
        "iso_alpha",
        "country",
        "country_ko",
        "continent_ko",
        "sample_count",
        "avg_score",
        "max_score",
        "avg_altitude_m",
        "top_archetype",
        "top_processing",
        *SENSORY_COLS,
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=out_cols)

    group_keys = ["iso_alpha"] if by_iso else ["country", "country_ko", "iso_alpha", "continent_ko"]
    rows: list[dict[str, object]] = []

    for keys, grp in df.groupby(group_keys, dropna=False, sort=False):
        if by_iso:
            iso_code = str(keys[0] if isinstance(keys, tuple) else keys)
            unique_ko = sorted(grp["country_ko"].dropna().unique().tolist())
            unique_en = sorted(grp["country"].dropna().unique().tolist())
            if iso_code == "USA" and len(unique_ko) > 1:
                country_ko_val = "미국 (하와이 포함)"
                country_en_val = "United States"
            else:
                country_ko_val = unique_ko[0] if unique_ko else iso_code
                country_en_val = unique_en[0] if unique_en else iso_code
            continent_val = _safe_mode(grp["continent_ko"], default="기타")
        else:
            country_en_val, country_ko_val, iso_code, continent_val = keys

        avg_alt = _safe_mean(grp["altitude_m"]) if "altitude_m" in grp.columns else float("nan")
        record: dict[str, object] = {
            "iso_alpha": str(iso_code),
            "country": str(country_en_val),
            "country_ko": str(country_ko_val),
            "continent_ko": str(continent_val),
            "sample_count": int(len(grp)),
            "avg_score": round(_safe_mean(grp["total_cup_points"]), 2),
            "max_score": round(float(pd.to_numeric(grp["total_cup_points"], errors="coerce").max()), 2),
            "avg_altitude_m": round(avg_alt, 1) if pd.notna(avg_alt) else float("nan"),
            "top_archetype": _safe_mode(grp["flavor_archetype"], default="스페셜티 밸런스"),
            "top_processing": _safe_mode(grp["processing_ko"], default="기타 / 미상"),
        }
        for col in SENSORY_COLS:
            val = _safe_mean(grp[col]) if col in grp.columns else float("nan")
            record[col] = round(val, 2) if pd.notna(val) else float("nan")
        rows.append(record)

    summary = pd.DataFrame(rows, columns=out_cols)
    return summary.sort_values(
        by=["avg_score", "sample_count", "country_ko"], ascending=[False, False, True]
    ).reset_index(drop=True)


def get_flavor_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Compute summary statistics across the 6 core sensory pillars for radar/bar charts.

    Handles empty or 1-row DataFrames safely (std_score defaults to 0.0 for 1 row).
    """
    out_cols = [
        "metric",
        "label_ko",
        "mean_score",
        "median_score",
        "std_score",
        "min_score",
        "max_score",
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=out_cols)

    rows: list[dict[str, object]] = []
    for col in SENSORY_COLS:
        if col not in df.columns:
            continue
        vals = pd.to_numeric(df[col], errors="coerce").dropna()
        if vals.empty:
            continue
        std_val = float(vals.std(ddof=1)) if len(vals) > 1 else 0.0
        rows.append(
            {
                "metric": col,
                "label_ko": SENSORY_LABELS_KO.get(col, col),
                "mean_score": round(float(vals.mean()), 2),
                "median_score": round(float(vals.median()), 2),
                "std_score": round(std_val, 3),
                "min_score": round(float(vals.min()), 2),
                "max_score": round(float(vals.max()), 2),
            }
        )
    return pd.DataFrame(rows, columns=out_cols)


def summarize_by_archetype(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate bean counts, percentage share, and average cup score by flavor archetype."""
    out_cols = [
        "flavor_archetype",
        "count",
        "share_pct",
        "avg_score",
        "description_ko",
    ]
    if df is None or df.empty or "flavor_archetype" not in df.columns:
        return pd.DataFrame(columns=out_cols)

    total = len(df)
    rows: list[dict[str, object]] = []
    for archetype, grp in df.groupby("flavor_archetype", dropna=False):
        name = str(archetype)
        cnt = int(len(grp))
        rows.append(
            {
                "flavor_archetype": name,
                "count": cnt,
                "share_pct": round((cnt / total) * 100.0, 1) if total > 0 else 0.0,
                "avg_score": round(_safe_mean(grp["total_cup_points"]), 2),
                "description_ko": ARCHETYPE_DESCRIPTIONS_KO.get(name, ""),
            }
        )
    return (
        pd.DataFrame(rows, columns=out_cols)
        .sort_values(by=["count", "avg_score"], ascending=[False, False])
        .reset_index(drop=True)
    )


def summarize_by_processing(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate bean counts and sensory scores by processing method."""
    out_cols = [
        "processing_ko",
        "processing_method",
        "count",
        "share_pct",
        "avg_score",
        "avg_acidity",
        "avg_body",
        "avg_sweetness",
    ]
    if df is None or df.empty or "processing_ko" not in df.columns:
        return pd.DataFrame(columns=out_cols)

    total = len(df)
    rows: list[dict[str, object]] = []
    for (proc_ko, proc_en), grp in df.groupby(["processing_ko", "processing_method"], dropna=False):
        cnt = int(len(grp))
        rows.append(
            {
                "processing_ko": str(proc_ko),
                "processing_method": str(proc_en),
                "count": cnt,
                "share_pct": round((cnt / total) * 100.0, 1) if total > 0 else 0.0,
                "avg_score": round(_safe_mean(grp["total_cup_points"]), 2),
                "avg_acidity": round(_safe_mean(grp["acidity"]), 2),
                "avg_body": round(_safe_mean(grp["body"]), 2),
                "avg_sweetness": round(_safe_mean(grp["sweetness"]), 2),
            }
        )
    return (
        pd.DataFrame(rows, columns=out_cols)
        .sort_values(by=["count", "avg_score"], ascending=[False, False])
        .reset_index(drop=True)
    )


def get_origin_story(country_name: str) -> str:
    """Return an editorial Korean origin story for either Korean or English country names."""
    if not country_name:
        return "커피 벨트 고유의 기후와 토양, 가공 전통이 어우러져 다채로운 스페셜티 향미를 만들어내는 산지입니다."
    key = str(country_name).strip()
    if key in ORIGIN_STORIES_KO:
        return ORIGIN_STORIES_KO[key]
    mapped_ko = _ENGLISH_TO_KO_COUNTRY.get(key)
    if mapped_ko and mapped_ko in ORIGIN_STORIES_KO:
        return ORIGIN_STORIES_KO[mapped_ko]
    if key == "미국 (하와이 포함)":
        return ORIGIN_STORIES_KO["미국 (하와이)"]
    return f"{key}는 고유의 테루아와 재배 환경이 어우러져 개성 있는 컵 프로파일을 선보이는 커피 벨트 산지입니다."
