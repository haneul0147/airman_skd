import pandas as pd
sheet_name = "2025_data"
DATE = 'ATA_DATE'
Flight_TYPE = "TYPE"

df = pd.read_excel(r"D:\Users\Airman02\Desktop\FX 자료정리\Transportation charge.2025year_thing.xlsx",sheet_name)

print(df.columns)

df_in = df[df[Flight_TYPE] == "IN"]
df_out = df[df[Flight_TYPE] == "OUT"]

df_in.to_excel(r"D:\Users\Airman02\Desktop\FX 자료정리\in_final.xlsx", index=False)
df_out.to_excel(r"D:\Users\Airman02\Desktop\FX 자료정리\out_final.xlsx", index=False)

print("완료")