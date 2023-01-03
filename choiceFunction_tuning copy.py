from createPreferenceKomabaTest import CreatePrefKomaba
from DAMaqKomaba import DAMaqKomaba
from import_data import facultyData
import pandas as pd
import numpy as np
import copy
from collections import OrderedDict as od
from numba import jit

minorityReserveB, minorityReserveDA, M, shiteiDict, fac, bunri, categoryToList=facultyData.main()

n=0
trial=1000
batch=10
multiply=0.1
flag=True
alpha=1
theta=1
karui={"l1":104,"l2":132,"l3":111,"s1":406,"s2":217,"s3":32}
karui_list=list(karui.keys())
submitter=[]
accepter=[]
for i in range(1002):
    submitter.append("student"+str(i+1))
accepter=["法学部", "経済学部", "文学部", "教育学部", "工学部", "理学部" ,"農学部", "医学部", "数理科学部", "薬学部"]
valueDF = pd.read_csv("value.csv", index_col=0, header=0)
valueDict = valueDF.to_dict()
tmp=np.load("fill.npy", allow_pickle=True)
fill_dict=tmp.item()


#選好の生成
def PrefSim():
    for n in range(10000):
        sData,aData, aData2, aData3=CreatePrefKomaba(karui,minorityReserveB, minorityReserveDA ,alpha,theta,M, accepter, submitter, n, valueDict=valueDict, isCutOff=False).main()

#choice_value
karuiValueDict=dict(zip(fac,[0 for _ in range(len(fac))]))
choiceValueDict=dict(zip(list(karui.keys()), [copy.deepcopy(karuiValueDict) for _ in range(6)]))
if flag==True:
    choiceValueDict=np.load("choiceValueDict.npy", allow_pickle=True).item()

#実データdict読み込み
tmp=np.load("quota_dict.npy", allow_pickle=True)
quota_dict=tmp.item()
tmp=np.load("zenkarui_dict.npy", allow_pickle=True)
zenkarui_dict=tmp.item()
tmp=np.load("shiteikarui_dict.npy", allow_pickle=True)
shiteikarui_dict=tmp.item()



for n in range(trial):
    shitei_dict_sim=dict()
    zenkarui_dict_sim=dict()
    for f in fac:
        shitei_dict_sim[f]={"l1":0,"l2":0,"l3":0,"s1":0,"s2":0,"s3":0}    #batchの更新に使う
        zenkarui_dict_sim[f]={"l1":0,"l2":0,"l3":0,"s1":0,"s2":0,"s3":0}    #batchの更新に使う
    for m in range(batch):
        numeric=n*10+m
        #preference生成
        CreatePrefKomaba(karui,minorityReserveB, minorityReserveDA ,alpha,theta,M, accepter, submitter, numeric, valueDict=valueDict, isCutOff=False).main()
        #preference_data読み込み

        preferenceDF=pd.read_csv(f"MultiThread/created_submit_komaba{numeric}.csv",header=0, index_col=0)

        #choice_function_tuning
        student_pref_dict=dict()
        student_karui_dict=dict()

        for student in  preferenceDF.index.values:
            student_data=preferenceDF.loc[student,:].dropna().to_list()
            student_karui=student_data[0]
            student_karui_dict[student]=student_karui
            student_pref=student_data[1:]
            utility_dict=dict()
            utility_dict=dict(zip(student_pref ,np.random.normal(0, 1, len(student_pref))))
            for f in student_pref:
                utility_dict[f]+=choiceValueDict[student_karui][f]
                utility_dict = sorted(utility_dict.items(), key=lambda x:x[1], reverse=True)
                utility_dict=od(utility_dict)
            student_pref_dict[student]=utility_dict
            
        dataframe_list=[]
        for student in list(student_pref_dict.keys()):
            temp=[]
            temp.append(student)
            temp.append(student_karui_dict[student])
            temp=temp+list(student_pref_dict[student].keys())
            dataframe_list.append(temp)
        df=pd.DataFrame(dataframe_list)
        df=df.rename({0:"submitter", 1:"karui", 2:"Preference"}, axis=1)
        df.set_index("submitter", inplace=True)
        df.to_csv(f"MultiThread/created_submit_komaba_choiced{numeric}.csv", encoding="utf-8-sig")
        DAMaqKomaba('MultiThread\created_submit_komaba_choiced'+str(numeric)+'.csv','MultiThread\created_accept_komaba'+str(numeric)+'.csv',numeric, filename='submitMaqResultKomabaChoiced'+str(numeric))

        fill_sim=np.load(f"MultiThread/sim_fill{numeric}.npy", allow_pickle=True).item()
        zenkarui_sim_df=pd.read_csv(f"MultiThread/majority_acceptance_MQ{numeric}.csv", header=None, index_col=0)
        for f in fac:
            accept_student=zenkarui_sim_df.loc[f].dropna().to_list()
            for student in accept_student:
                student_karui=student_karui_dict[student]
                zenkarui_dict_sim[f][student_karui]+=1
        for f in fac:
            karui_keys=list(fill_sim[f].keys()  )
            for k in karui_keys:
                accept_student=fill_sim[f][k]
                for student in accept_student:
                    student_karui=student_karui_dict[student]
                    shitei_dict_sim[f][student_karui]+=1

    #平均に起こす
    avg_shitei_dict=copy.deepcopy(shitei_dict_sim)
    avg_zenkarui_dict=copy.deepcopy(zenkarui_dict_sim)
    for f in fac:
        for k in karui_list:
            avg_shitei_dict[f][k]=avg_shitei_dict[f][k]/batch
            avg_zenkarui_dict[f][k]=avg_zenkarui_dict[f][k]/batch
    regret=0
    #罰則項を反映
    for f in fac:
        for k in karui_list:
            # if shiteikarui_dict[f][k] != 0:
            #     choiceValueDict[k][f]+=multiply*(shiteikarui_dict[f][k]-avg_shitei_dict[f][k])
            #     regret+=abs(multiply*(shiteikarui_dict[f][k]-avg_shitei_dict[f][k]))
            # else:
            #     choiceValueDict[k][f]+=-multiply*avg_shitei_dict[f][k]
            #     regret+=abs(-multiply*avg_shitei_dict[f][k])
            if zenkarui_dict[f][k] != 0:
                choiceValueDict[k][f]+=multiply*(zenkarui_dict[f][k]-avg_zenkarui_dict[f][k])
                regret+=abs(multiply*(zenkarui_dict[f][k]-avg_zenkarui_dict[f][k]))
            else:
                choiceValueDict[k][f]+=-multiply*avg_zenkarui_dict[f][k]
                regret+=abs(-multiply*avg_zenkarui_dict[f][k])
    print(f"現在の試行回数{n}回目",regret/multiply)
    np.save("choiceValueDict_zen.npy",choiceValueDict)