import pandas as pd
sheet_name = "OUT"
DATE_COL = 'FLIGHT_DATE'
DUP_COL = "FLT_NBR"
FLIGHT_TYPE = "TYPE"
PATH = r"D:\Users\Airman02\Desktop\FX 자료정리\in_final.xlsx" 

df = pd.read_excel(PATH,sheet_name)
print(df.columns)

original_count = len(df)

duplicated_rows = df[df.duplicated(
        subset=[DATE_COL, DUP_COL],
        keep='first'
    )]

duplicated_count = len(duplicated_rows)

# 중복 제거
df_dedup = df.drop_duplicates(
        subset=[DATE_COL, DUP_COL],
        keep='first'
    )

final_count = len(df_dedup)

print(f"원본 행 수        : {original_count}")
print(f"중복 제거된 행 수 : {duplicated_count}")
print(f"최종 행 수        : {final_count}")
print(f"검증(original - duplicated == final) → "
          f"{original_count - duplicated_count == final_count}")

# df = df.drop_duplicates(
#     subset=[DATE, FLT],  # 👈 기준 컬럼
#     keep='first')

# # dup = df[df.duplicated(subset=[DATE], keep=False)]

# dup.to_excel(r"D:\Users\Airman02\Desktop\FX 자료정리\in_duplicates_false.xlsx", index=False)
# df.to_excel(r"D:\Users\Airman02\Desktop\FX 자료정리\in_duplicatesOUT.xlsx", index=False)
