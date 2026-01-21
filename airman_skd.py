# app.py
import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime

# ---------------------------
# 페이지 설정
# ---------------------------
st.set_page_config(
    page_title="스케줄 정렬 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.title("📅 출/입국 스케줄 정렬")

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
        match = re.match(r"^([가-힣]+)", line)
        if match:
            current_worker = match.group(1)  # 맨 앞 한글 이름만 가져오기
            print(current_worker)
            continue
        
        # 맨 앞 번호 제거
        line = re.sub(r"^\d+\.?\s*", "", line)
        flight = re.match(r"([A-Za-z0-9]{2}\d+)", line, re.IGNORECASE)
        people = re.search(r"(\d+)명", line)
        io = re.search(r"(입|출)", line)
        time_match = re.search(r"(\d{2}:\d{2})", line)
        
        time_val = time_match.group(1).replace(";", ":") if time_match else ""
        # hotel = "SH" if "/sh" in line.lower() else "SIH"
        
        #srt 또는 sih로 호텔 적어놓거나 안적는 경우
        line_lower = line.lower()
        if "/sh" in line_lower:
            print("sh은 "+line_lower)
            hotel = "SH"
            
        elif any(k in line_lower for k in ["/srt", "/sih"]):
            print("SIH은 " + line_lower)
            hotel = "SIH"
        else:
            hotel = "SIH"  # 기본값
        
         # 🔥 비고 단어 체크 (hotel 뒤에 spot/지원/스팟 있으면 제외)
        # exclude_keywords = ["spot", "지원", "스팟",]
        # if any(k.lower() in line.lower() for k in exclude_keywords):
        #     continue  # 해당 행은 제외
        
        if flight and io and io.group(1) == io_type:
            schedule.append({
                "근무자": current_worker,
                "편명": flight.group(1),
                "인원": int(people.group(1)) if people else 1,
                "시간": time_val,
                "호텔": hotel,
                "입/출국": io_type,
            })
    return pd.DataFrame(schedule)

# ---------------------------
# 2️⃣ 탭 구성
# ---------------------------
tab1, tab2 = st.tabs(["✈️ 공항서비스팀 출국 스케줄", "🛬 FX 입국 스케줄"])

# ---------------------------
# 출국 FX/5X 스케줄
# ---------------------------
with tab1:
    st.subheader("출국 스케줄 (FX만 표시)")
    text_out = st.text_area("출국 스케줄 텍스트 붙여넣기", height=250)
    file_out = st.file_uploader("또는 출국 스케줄 엑셀 업로드", type=["xlsx"], key="outbound")

    if st.button("📊 출국 FX/5X 스케줄 정렬 실행"):
        if text_out.strip():
            df_out = parse_schedule(text_out, io_type="출")
        elif file_out:
            df_out = pd.read_excel(file_out)
            df_out = df_out[df_out["입/출국"].str.lower() == "출"].copy()
        else:
            df_out = pd.DataFrame()

        if not df_out.empty:
            # FX 또는 5X 편명만 필터링
            df_out = df_out[df_out['편명'].str.upper().str.match(r'^(FX|5X)')].copy()
            if df_out.empty:
                st.info("FX 또는 5X 편명이 존재하지 않습니다.")
            else:
                # 근무자 이름 알파벳순 정렬
                df_out['근무자'] = df_out['근무자'].apply(lambda x: ", ".join(sorted([n.strip() for n in x.split(",")])))
                #print(df_out)
                # 시간 기준 정렬
                df_out['시간_dt'] = pd.to_datetime(df_out['시간'], format="%H:%M", errors='coerce')
                df_out = df_out.sort_values(['시간_dt','편명']).drop(columns='시간_dt').reset_index(drop=True)
                print(df_out)
                # 번호 추가
                df_out.index += 1
                df_out.insert(0, "번호", df_out.index)
                
                #인원 "명" 표시하기
                df_out['인원'] = df_out['인원'].astype(str) + "명"
                
                df_out = df_out[["번호", "편명", "인원", "시간", "호텔", "근무자"]]

                st.dataframe(df_out, use_container_width=True)

                # 엑셀 다운로드
                buffer_out = BytesIO()
                with pd.ExcelWriter(buffer_out, engine="xlsxwriter") as writer:
                    df_out.to_excel(writer, index=False, sheet_name="출국FX5X스케줄")
                st.download_button(
                    "⬇️ 출국 FX/5X 스케줄 엑셀 다운로드",
                    buffer_out.getvalue(),
                    file_name="출국_FX5X_스케줄.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("텍스트를 붙여넣거나 엑셀을 업로드해 주세요.")

# ---------------------------
# 입국 FX/5X 스케줄
# ---------------------------
with tab2:
    st.subheader("입국 스케줄 (FX만 표시)")
    text_in = st.text_area("입국 스케줄 텍스트 붙여넣기", height=250)
    file_in = st.file_uploader("또는 입국 스케줄 엑셀 업로드", type=["xlsx"], key="inbound")

    if st.button("📊 입국 FX 스케줄 정렬 실행"):
        if text_in.strip():
            df_in = parse_schedule(text_in, io_type="입")
        elif file_in:
            df_in = pd.read_excel(file_in)
            df_in = df_in[df_in["입/출국"].str.lower() == "입"].copy()
        else:
            df_in = pd.DataFrame()

        if not df_in.empty:
            # FX 편명만 필터링
            df_in = df_in[df_in['편명'].str.upper().str.match(r'^(FX)')].copy()

            if df_in.empty:
                st.info("FX 편명이 존재하지 않습니다.")
            else:
                # 근무자 이름 알파벳순 정렬
                df_in['근무자'] = df_in['근무자'].apply(lambda x: ", ".join(sorted([n.strip() for n in x.split(",")])))

                # 🔥 같은 편명 + 호텔 기준으로 근무자 합치기
                df_in = df_in.groupby(['편명'], as_index=False).agg({
                '근무자': lambda x: ", ".join(sorted(set(x))),  # 중복 제거 후 합치기
                '인원': 'sum',  # 인원 합산
                '시간': 'min'   # 가장 빠른 시간 사용
                })
                #print(df_in)
                
                # 시간 기준 정렬
                df_in['시간_dt'] = pd.to_datetime(df_in['시간'], format="%H:%M", errors='coerce')
                df_in = df_in.sort_values(['시간_dt',"편명"]).reset_index(drop=True)
                

                # 번호 추가
                df_in.index += 1
                df_in.insert(0, "번호", df_in.index)
                
                #인원 "명" 표시하기
                df_in['인원'] = df_in['인원'].astype(str) + "명"
                #print(df_in)
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

# ---------------------------
# 3️⃣ 탭 버튼 CSS (PC/모바일 대응)
# ---------------------------
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