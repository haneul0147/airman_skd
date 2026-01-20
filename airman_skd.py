import streamlit as st
import pandas as pd
import re
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="스케줄 정렬 대시보드", layout="wide")
st.title("📅 출/입국 스케줄 정렬 대시보드")

# -----------------------------
# 탭 생성
tab1, tab2 = st.tabs(["✈️ 출국 스케줄", "🛬 입국 FX 스케줄"])

# =============================
# 출국 스케줄 (모든 편명)
# =============================
with tab1:
    st.subheader("출국 스케줄 (공항서비스 전달용)")
    text_out = st.text_area("출국 스케줄 텍스트 붙여넣기", height=250)
    file_out = st.file_uploader("또는 출국 스케줄 엑셀 업로드", type=["xlsx"], key="outbound")

    if st.button("📊 출국 스케줄 정렬 실행"):
        schedule_out = []
        current_worker_out = ""

        # 텍스트 처리
        if text_out.strip():
            lines = text_out.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if re.match(r"^[가-힣]+$", line):
                    current_worker_out = line
                    continue
                line = re.sub(r"^\d+\.\s*", "", line)
                flight = re.search(r"[A-Za-z0-9]+", line)
                people = re.search(r"(\d+)명", line)
                io = re.search(r"(입|출)", line)
                hotel = "SH" if "/sh" in line.lower() else "SIH"
                time_match = re.search(r"(\d{2}:\d{2})", line)
                time_val = time_match.group(1) if time_match else ""
                if flight and people and io and io.group(1) == "출":
                    schedule_out.append({
                        "근무자": current_worker_out,
                        "편명": flight.group(),
                        "인원": int(people.group(1)),
                        "호텔": hotel,
                        "시간": time_val
                    })

        # 엑셀 업로드 처리
        if file_out:
            df_out = pd.read_excel(file_out)
            df_out = df_out[df_out["입/출국"] == "출"].copy()
            df_out['호텔'] = df_out['호텔'].replace("", "SIH")
        elif schedule_out:
            df_out = pd.DataFrame(schedule_out)
        else:
            df_out = None

        if df_out is not None and not df_out.empty:
            # 같은 편명 + 시간 + 호텔 근무자 합치기
            df_grouped = (
                df_out.groupby(["편명", "시간", "호텔"], as_index=False)
                .agg({
                    "근무자": lambda x: ", ".join(sorted(x)),
                    "인원": "sum"
                })
            )
            # 시간 기준 정렬
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

# =============================
# 입국 FX 스케줄
# =============================
with tab2:
    st.subheader("입국 스케줄 (FX INBOUND 전달 용)")
    text_in = st.text_area("입국 스케줄 텍스트 붙여넣기", height=250)
    file_in = st.file_uploader("또는 입국 스케줄 엑셀 업로드", type=["xlsx"], key="inbound")

    if st.button("📊 입국 스케줄 정렬 실행"):
        schedule_in = []
        current_worker_in = ""

        # 텍스트 처리
        if text_in.strip():
            lines = text_in.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if re.match(r"^[가-힣]+$", line):
                    current_worker_in = line
                    continue
                line = re.sub(r"^\d+\.\s*", "", line)
                flight = re.search(r"[A-Za-z0-9]+", line)
                io = re.search(r"(입|출)", line)
                if flight and io and io.group(1) == "입" and "FX" in flight.group().upper():
                    schedule_in.append({
                        "근무자": current_worker_in,
                        "편명": flight.group(),
                        "시간": re.search(r"(\d{2}:\d{2})", line).group(1) 
                                 if re.search(r"(\d{2}:\d{2})", line) else ""
                    })

        # 엑셀 업로드 처리
        if file_in:
            df_in = pd.read_excel(file_in)
            df_in = df_in[(df_in["입/출국"].str.lower() == "입") & (df_in["편명"].str.upper().str.contains("FX"))][["편명", "근무자", "시간"]]
        elif schedule_in:
            df_in = pd.DataFrame(schedule_in)
        else:
            df_in = None

        if df_in is not None and not df_in.empty:
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