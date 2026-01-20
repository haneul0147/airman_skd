import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="출국 스케줄 정렬 대시보드", layout="wide")
st.title("✈️ 출국 스케줄 시간순 정렬 (편명 기준)")

# -----------------------------
# 1️⃣ 데이터 입력: 엑셀 or 텍스트
# -----------------------------
tab1, tab2 = st.tabs(["📄 엑셀 업로드", "📝 텍스트 붙여넣기"])
df = None

with tab1:
    file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])
    if file:
        df = pd.read_excel(file)

with tab2:
    text = st.text_area("여기에 스케줄 텍스트를 붙여넣으세요", height=300)
    if text.strip():
        lines = text.splitlines()
        schedule = []
        current_worker = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 근무자 이름
            if re.match(r"^[가-힣]+$", line):
                current_worker = line
                continue

            # 맨 앞 "1. ", "2. " 제거
            line = re.sub(r"^\d+\.\s*", "", line)

            # 편명, 인원, 입/출국, 시간, 호텔 추출
            flight = re.search(r"[A-Za-z0-9]+", line)
            people = re.search(r"(\d+)명", line)
            io = re.search(r"(입|출)", line)
            time_match = re.search(r"(\d{2}:\d{2})", line)
            hotel = "SH" if "/sh" in line.lower() else ""

            if flight and people and io and time_match:
                schedule.append({
                    "근무자": current_worker,
                    "편명": flight.group(),
                    "인원": int(people.group(1)),
                    "입/출국": io.group(1),
                    "시간": time_match.group(1),
                    "호텔": hotel
                })

        df = pd.DataFrame(schedule)

# -----------------------------
# 2️⃣ 출국만 필터 & 시간순 정렬
# -----------------------------
if df is not None and not df.empty:
    st.subheader("✈️ 출국 스케줄 시간순 정렬 (편명 기준)")

    df_out = df[df["입/출국"] == "출"].copy()

    # -----------------------------
    # 3️⃣ 같은 편명인 경우 근무자 이름 합치기
    # -----------------------------
    df_grouped = (
        df_out.groupby(["편명", "시간", "호텔"], as_index=False)
        .agg({
            "근무자": lambda x: ", ".join(sorted(x)),
            "인원": "sum",
            "입/출국": "first"
        })
    )

    # 시간 기준 정렬
    df_grouped["시간_dt"] = pd.to_datetime(df_grouped["시간"], format="%H:%M")
    df_grouped = df_grouped.sort_values("시간_dt").drop(columns="시간_dt")

    st.dataframe(df_grouped, use_container_width=True)

    # -----------------------------
    # 4️⃣ 엑셀 다운로드
    # -----------------------------
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_grouped.to_excel(writer, index=False, sheet_name="출국스케줄")
    st.download_button(
        "⬇️ 출국 스케줄 엑셀 다운로드",
        buffer.getvalue(),
        file_name="출국_스케줄_정렬.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("엑셀을 업로드하거나 텍스트를 붙여넣어 주세요.")