# app.py
import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="스케줄 정렬 대시보드", layout="wide",initial_sidebar_state="collapsed")
st.title("📅 출/입국 스케줄 정렬 ")


# ---------------------------
# 1️⃣ 캐싱 함수
# ---------------------------
@st.cache_data
def parse_schedule(text, io_type="출"):
    schedule = []
    current_worker = ""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # 근무자 이름
        if re.match(r"^[가-힣]+$", line):
            current_worker = line
            continue
        # 맨 앞 번호 제거
        line = re.sub(r"^\d+\.\s*", "", line)
        flight = re.search(r"[A-Za-z0-9]+", line)
        people = re.search(r"(\d+)명", line)
        io = re.search(r"(입|출)", line)
        time_match = re.search(r"(\d{2}:\d{2})", line)
        hotel = "SH" if "/sh" in line.lower() else "SIH"
        time_val = time_match.group(1) if time_match else ""
        if flight and io and io.group(1) == io_type:
            schedule.append({
                "근무자": current_worker,
                "편명": flight.group(),
                "인원": int(people.group(1)) if people else 1,
                "시간": time_val,
                "호텔": hotel
            })
    return pd.DataFrame(schedule)

# ---------------------------
# 2️⃣ 탭 구성
# ---------------------------
tab1, tab2 = st.tabs(["✈️ 공항서비스(출국) 스케줄", "🛬 FX 입국 스케줄"])

# ---------------------------
# 출국 스케줄
# ---------------------------
with tab1:
    st.subheader("출국 스케줄 (공항서비스팀 아웃바운드 공유)")
    text_out = st.text_area("출국 스케줄 텍스트 붙여넣기", height=250)
    file_out = st.file_uploader("또는 출국 스케줄 엑셀 업로드", type=["xlsx"], key="outbound")

    if st.button("📊 출국 스케줄 정렬 실행"):
        # 텍스트 처리
        if text_out.strip():
            df_out = parse_schedule(text_out, io_type="출")
        elif file_out:
            df_out = pd.read_excel(file_out)
            df_out = df_out[df_out["입/출국"].str.lower() == "출"].copy()
            df_out['호텔'] = df_out['호텔'].replace("", "SIH")
        else:
            df_out = pd.DataFrame()

        if not df_out.empty:
            # 편명, 시간, 호텔 기준으로 그룹화
            df_grouped = (
                df_out.groupby(["편명", "시간", "호텔"], as_index=False)
                .agg({
                    "근무자": lambda x: ", ".join(sorted(x)),
                    "인원": "sum"
                })
            )
            df_grouped['시간_dt'] = pd.to_datetime(df_grouped['시간'], format="%H:%M", errors='coerce')
            df_grouped = df_grouped.sort_values('시간_dt').drop(columns='시간_dt').reset_index(drop=True)
            df_grouped.index += 1
            df_grouped.insert(0, "번호", df_grouped.index)
            df_grouped = df_grouped[["번호", "편명", "인원", "시간", "호텔", "근무자"]]

            st.dataframe(df_grouped, use_container_width=True)

            # 엑셀 다운로드
            buffer_out = BytesIO()
            with pd.ExcelWriter(buffer_out, engine="xlsxwriter") as writer:
                df_grouped.to_excel(writer, index=False, sheet_name="출국스케줄")
            st.download_button(
                "⬇️ 출국 스케줄 엑셀 다운로드",
                buffer_out.getvalue(),
                file_name="출국_스케줄.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("텍스트를 붙여넣거나 엑셀을 업로드해 주세요.")

# ---------------------------
# 입국 FX 스케줄
# ---------------------------
with tab2:
    st.subheader("입국 스케줄 (FX 인바운드 담당자공유)")
    text_in = st.text_area("입국 스케줄 텍스트 붙여넣기", height=250)
    file_in = st.file_uploader("또는 입국 스케줄 엑셀 업로드", type=["xlsx"], key="inbound")

    if st.button("📊 입국 FX 스케줄 정렬 실행"):
        # 텍스트 처리
        if text_in.strip():
            df_in = parse_schedule(text_in, io_type="입")
            # FX만 필터링 (대소문자 무시)
            df_in = df_in[df_in['편명'].str.upper().str.contains("FX")]
        elif file_in:
            df_in = pd.read_excel(file_in)
            df_in = df_in[(df_in["입/출국"].str.lower() == "입") & 
                          (df_in["편명"].str.upper().str.contains("FX"))]
        else:
            df_in = pd.DataFrame()

        if not df_in.empty:
            df_in['시간_dt'] = pd.to_datetime(df_in['시간'], format="%H:%M", errors='coerce')
            df_in = df_in.sort_values('시간_dt').drop(columns='시간_dt').reset_index(drop=True)
            df_in.index += 1
            df_in.insert(0, "번호", df_in.index)
            df_in = df_in[["번호", "편명", "근무자"]]

            st.dataframe(df_in, use_container_width=True)

            # 엑셀 다운로드
            buffer_in = BytesIO()
            with pd.ExcelWriter(buffer_in, engine="xlsxwriter") as writer:
                df_in.to_excel(writer, index=False, sheet_name="입국FX스케줄")
            st.download_button(
                "⬇️ 입국 FX 스케줄 엑셀 다운로드",
                buffer_in.getvalue(),
                file_name="입국_FX_스케줄.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("텍스트를 붙여넣거나 엑셀을 업로드해 주세요.")
            
            
st.markdown("""
<style>

/* 탭 버튼 */
button[data-testid="stTab"] {
    font-size: 55px !important;
    padding: 20px 35px !important;
}

/* 모바일 */
@media (max-width: 768px) {
    button[data-testid="stTab"] {
        font-size: 15px !important;
        padding: 12px 14px !important;
        white-space: normal !important;
        text-align: center;
    }
}

</style>
""", unsafe_allow_html=True)