import pandas as pd
from import_data import facultyData
minorityReserveB, minorityReserveDA, M, shiteiDict, fac, bunri, categoryToList=facultyData.main()
fill_data=dict()
for f in fac:
    fill_data[f]=[0, 0] #mr, mq
for i in range(1000):
    fill_mir_df = pd.read_csv(f"MultiThread/fill_rate_mir{i}.csv", header=0, index_col=0)
    fill_Maq_df = pd.read_csv(f"MultiThread/fill_rate_Maq{i}.csv", header=0, index_col=0)
    for f in fac:
        fill_data[f][0] += fill_mir_df.loc[f, "fill rate"]
        fill_data[f][1] += fill_Maq_df.loc[f, "fill rate"]
        
for f in fac:
    fill_data[f][0] = fill_data[f][0]/1000
    fill_data[f][1] = fill_data[f][1]/1000
        
df = pd.DataFrame(list(fill_data.values()), columns=["MRの定員充足率", "MQの定員充足率"], index=list(fill_data.keys()))
print(df)
df.to_csv("fill_rate.csv", encoding="utf-8-sig")