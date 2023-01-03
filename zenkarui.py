#選好パラメタ
from createPreferenceKomabaTest import CreatePrefKomaba
from import_data import facultyData
import pandas as pd
import copy
import numpy as np 
import math
karui={"l1":104,"l2":132,"l3":111,"s1":406,"s2":217,"s3":32}
submitN={"l1":417,"l2":999,"l3":978,"s1":3712,"s2":2016,"s3":36}
minorityReserveB, minorityReserveDA, M ,shiteiDict, fac, bunri, categoryToList=facultyData.main()
def createPref(karui, alpha, theta, n, type, valueDict):
    minorityReserveB, minorityReserveDA, M ,shiteiDict, fac, bunri, categoryToList=facultyData.main()
    submitter = list()
    for i in range(1002):
        submitter.append("student"+str(i+1))
    sData,aData, aData2, aData3=CreatePrefKomaba(karui=karui,minorityReserveB=minorityReserveB,minorityReserveDA=minorityReserveDA, alpha=alpha, theta=theta, M=0, alist=[], slist=submitter, n=n, valueDict=valueDict, isCutOff=True).main()
    if type=="MR":
        return aData2, aData3
    elif type=="submit":
        return sData
    elif type=="preference":
        return aData
    elif type=="all":
        return sData,aData, aData2, aData3



batch=5
karuiValueDict=dict(zip(fac,[0 for _ in range(len(fac))]))
valueDict=dict(zip(list(karui.keys()), [copy.deepcopy(karuiValueDict) for _ in range(6)]))
for n in range(2000):
    karuiCorrectionDict=dict(zip(fac,[0 for _ in range(len(fac))]))
    CorrectionDict=dict(zip(list(karui.keys()), [copy.deepcopy(karuiCorrectionDict) for _ in range(6)]))
    for m in range(batch):
        regret = 0
        number = n*batch + m
        print(f"now is {number}th process")
        studentPreference = createPref(karui, 0.8, 1, number, "submit", valueDict)
        studentPreference = studentPreference.iloc[1:, 1:]
        row, col = studentPreference.shape
        facultyDict={k:{"l1":0, "l2":0, "l3":0, "s1":0, "s2":0, "s3":0} for k in fac}
        for r in range(row):
            submit=studentPreference.iloc[r, :].to_list()
            for f in fac:
                if f in submit[1:]:
                    facultyDict[f][submit[0]] += 1
        df_list=[]
        for f in fac:
            tmp=[]
            faculty=facultyDict[f]
            tmp.append(f)
            for v in faculty.values():
                tmp.append(v)
            df_list.append(tmp)

        df=pd.DataFrame(df_list)
        df.columns=["学科","l1","l2","l3","s1","s2","s3"]
        df.index=df["学科"]
        df=df.drop("学科", axis=1)

        new_row=[]
        for col in df.columns.to_list():
            new_row.append(df[col].sum())
        df.loc["合計"]=new_row

        if m==4:
            df.to_csv("テスト.csv", encoding="utf-8-sig")

        teacher = pd.read_csv("申請.csv", header=0, index_col=0)

        idx=teacher.index
        idx = idx.drop("合計")
        col=teacher.columns
        for i in idx:
            for j in col:
                teacher_value = teacher.at[i, j]
                df_value = df.at[i, j]
                if teacher_value == 0:
                    correction_value = 0.1 * np.sign(teacher_value - df_value)
                    if math.isnan(correction_value):
                        correction_value = 0
                else:
                    correction_value = (teacher_value - df_value)/(teacher_value * 10)
                regret += abs(correction_value)
                CorrectionDict[j][i] += correction_value
    for i in idx:
        for j in col:
            valueDict[j][i] += CorrectionDict[j][i]/batch
    df_value = pd.DataFrame(valueDict)
    df_value.to_csv("value.csv", encoding="utf-8-sig")
print(regret)