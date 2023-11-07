import pandas as pd
from DAMaqKomaba import DAMaqKomaba
from DAmiRKomaba import DAmiRKomaba
from createPreferenceKomaba import CreatePrefKomaba
from choiceFunction import choice_function
from DAmiRKomaba import DAmiRKomaba
from DAMaqKomaba import DAMaqKomaba
from analyze import analyze
import time
import numpy as np
from import_data import facultyData
from concurrent.futures import ProcessPoolExecutor
import copy
#parameter
karui={"l1":104,"l2":132,"l3":111,"s1":406,"s2":217,"s3":32}
karuiList=["l1", "l2", "l3", "s1", "s2", "s3"]
m=20 #受け入れ者数
flag=True
isCutOff=False
if flag == True:
    choice_str="_choiced"
else:
    choice_str=""
#受け入れ定員
#p=0.2 #マイノリティ割合
#r=0.2 #マイノリティリザーブの割合
trial=1000 #試行回数
alpha=0.8 #生徒側の選好相関係数
theta=1 #学部側の選好相関係数
minorityReserveB, minorityReserveDA, M, shiteiDict, fac, bunri, categoryToList=facultyData.main()
##########
submitter=[]
accepter=[]
for i in range(1002):
    submitter.append("student"+str(i+1))
accepter=["法学部", "経済学部", "文学部", "教育学部", "工学部", "理学部" ,"農学部", "医学部", "数理科学部", "薬学部"]
startall=time.time()
result=[]
result.append(["karui", "b0", "b1", "b2", "b3", "b4", "w0", "w1", "w2", "w3", "w4"])
#karuiBetterDict=dict(zip(karuiList,listValue))
#karuiWorseDict=dict(zip(karuiList2,listValue2))
karuiBetterDict=dict()
for i in karuiList:
    karuiBetterDict[i]=[]
karuiWorseDict=dict()
for i in karuiList:
    karuiWorseDict[i]=[]
    
leaveKaruiAllDict=dict()
for i in ["MR", "MQ"]:
    temp=dict()
    for j in karuiList:
        temp[j]=[]
    leaveKaruiAllDict[i]=temp

valueDF = pd.read_csv("import/value.csv", index_col=0, header=0)
valueDict = valueDF.to_dict()


def simulation(n):
    start=time.time() #開始時間を記録します。
    test=CreatePrefKomaba(karui,minorityReserveB, minorityReserveDA ,alpha,theta,M, accepter, submitter, n, valueDict=valueDict, isCutOff=isCutOff).main()
    if flag==True:
        test0_5=choice_function(n, "import/choiceValueDict_smallest.npy").main()
    # process_time=time.time()-start #終わった時の時間から開始時間を引いて、startとこの変数の間の処理時間を算出します。
    # print("選好の生成までにかかった時間は"+str(process_time)+"秒です")
    test2=DAmiRKomaba('MultiThread\created_submit_komaba'+choice_str+str(n)+'.csv','MultiThread\created_accept_komaba'+str(n)+'.csv',n, filename='submitmirResultKomaba'+str(n))
    # process_time=time.time()-start #終わった時の時間から開始時間を引いて、startとこの変数の間の処理時間を算出します。
    # print("Minority reserve までにかかった時間は"+str(process_time)+"秒です")
    test3=DAMaqKomaba('MultiThread\created_submit_komaba'+choice_str+str(n)+'.csv','MultiThread\created_accept_komaba'+str(n)+'.csv',n, filename='submitMaqResultKomaba'+str(n))
    # process_time=time.time()-start #終わった時の時間から開始時間を引いて、startとこの変数の間の処理時間を算出します。
    # print("Majority quotaまでにかかった時間は"+str(process_time)+"秒です")
    betterWorseList, utilityMinusDict, mirCount, maqCount, leaveKaruiDict, dfFRmir, dfFRMaq=analyze('MultiThread\created_submit_komaba'+choice_str+str(n)+'.csv', 'MultiThread\submitmirResultKomaba'+str(n)+'.csv', 'MultiThread\submitMaqResultKomaba'+str(n)+'.csv','MultiThread\created_accept_komaba'+str(n)+'.csv', n).main()
    # process_time=time.time()-start #終わった時の時間から開始時間を引いて、startとこの変数の間の処理時間を算出します。
    # print("分析全体にかかった時間は"+str(process_time)+"秒です")
    print(str(n+1)+'回目終了')
    return betterWorseList, utilityMinusDict, mirCount, maqCount, leaveKaruiDict, dfFRmir, dfFRMaq
    # print(str(i+1)+'回目終了')
if __name__=="__main__":
    future_list=[]
    fill_rate_dict=dict()
    for f in fac:
        fill_rate_dict[f]=np.array([0, 0])
    with ProcessPoolExecutor() as executor:
        future=executor.map(simulation, range(trial), timeout=None)
        returnFuture=future
        mirCountAll=0
        maqCountAll=0
        leaveKaruiDictSum=dict()
        for k in karuiList:
            leaveKaruiDictSum[k] = {"MR":[], "MQ":[]}
        for i in returnFuture:
            betterWorseList, utilityMinusDict, mirCount, maqCount, leaveKaruiDict, dfFRmir, dfFRMaq=i

            dfFRmir=dfFRmir.set_index("faculty")
            dfFRMaq=dfFRMaq.set_index("faculty")

            for type in karuiList:
                karuiValueB=karuiBetterDict[type]
                karuiValueB.append(betterWorseList[type][0])
                karuiValueW=karuiWorseDict[type]
                karuiValueW.append(betterWorseList[type][1])
                
            utilityMinusDictSum=dict()
            for f in fac: #初期値
                utilityMinusDictSum[f]=np.array([0.0, 0.0, 0.0]) #指定科類、他、全部
            for f in fac:
                utilityMinusDictSum[f]+=utilityMinusDict[f]
            mirCountAll+=mirCount
            maqCountAll+=maqCount
            for f in fac:
                fill_rate_dict[f][0]+=dfFRmir.at[f, "fill rate"]
                fill_rate_dict[f][1]+=dfFRMaq.at[f, "fill rate"]
            for k in karuiList:
                leaveKaruiAllDict["MR"][k].append(leaveKaruiDict[k][0])
                leaveKaruiAllDict["MQ"][k].append(leaveKaruiDict[k][1])
        for f in fac:
            facQuota=M[f]["first"]+M[f]["second"]
            # if list(minorityReserveDA[f].values())[0]!=0:
            #     utilityMinusDictSum[f][0]=utilityMinusDictSum[f][0]/list(minorityReserveDA[f].values())[0]
            # else:
            #     utilityMinusDictSum[f][0]=0
            # utilityMinusDictSum[f][1]=utilityMinusDictSum[f][1]/(M[f]["second"]-list(minorityReserveDA[f].values())[0])
            # utilityMinusDictSum[f][2]=utilityMinusDictSum[f][2]/M[f]["second"]
            utilityMinusDictSum[f]=utilityMinusDictSum[f]/M[f]["second"]
    utilitySum=pd.DataFrame(list(utilityMinusDictSum.values()),columns=["指定科類枠の効用増減","全科類枠の効用増減", "全体での効用増減"], index=list(utilityMinusDictSum.keys()))
    utilitySum.to_csv("Result/utilitySum.csv", encoding='utf-8-sig')

        
    for type in karuiList:
        karuiBetterDict[type].sort()
        karuiWorseDict[type].sort()
    for type in karuiList:
        worst=0
        quarter=round(len(karuiBetterDict[type])/4)-1
        mean=round(len(karuiBetterDict[type])/2)-1
        thirdquarter=round(len(karuiBetterDict[type])*3/4)-1
        best=-1
        print(karuiBetterDict[type][worst]*100/karui[type], karuiBetterDict[type][quarter]*100/karui[type], karuiBetterDict[type][mean]*100/karui[type],karuiBetterDict[type][thirdquarter]*100/karui[type], karuiBetterDict[type][best]*100/karui[type])
        print(karuiWorseDict[type][worst]*100/karui[type],karuiWorseDict[type][quarter]*100/karui[type],karuiWorseDict[type][mean]*100/karui[type],karuiWorseDict[type][thirdquarter]*100/karui[type],karuiWorseDict[type][best]*100/karui[type])
        resultEachStep=[
            type,
            karuiBetterDict[type][worst]*100/karui[type], karuiBetterDict[type][quarter]*100/karui[type], karuiBetterDict[type][mean]*100/karui[type],karuiBetterDict[type][thirdquarter]*100/karui[type], karuiBetterDict[type][best]*100/karui[type],
            karuiWorseDict[type][worst]*100/karui[type],karuiWorseDict[type][quarter]*100/karui[type],karuiWorseDict[type][mean]*100/karui[type],karuiWorseDict[type][thirdquarter]*100/karui[type],karuiWorseDict[type][best]*100/karui[type],
        ]
        result.append(resultEachStep)
    result.append(["sum","","","","","","",mirCountAll/trial,maqCountAll/trial])
    resultcsv=pd.DataFrame(result)
    resultcsv.to_csv('Result/resultKomaba.csv', header=0, index=0, encoding="utf-8-sig")
    karuiBetterdf=pd.DataFrame(karuiBetterDict)
    karuiBetterdf.to_csv("Result/改善者.csv", encoding="utf-8-sig")
    karuiWorsedf=pd.DataFrame(karuiWorseDict)
    karuiWorsedf.to_csv("Result/悪化者.csv", encoding="utf-8-sig")
    
    for f in fac:
        fill_rate_dict[f]=fill_rate_dict[f]/trial
    fill_rate_df=pd.DataFrame(list(fill_rate_dict.values()), columns=["MRの定員充足率", "MQの定員充足率"])
    fill_rate_df.to_csv("Result/fill_rate.csv", encoding="utf-8-sig")
    
    decrease_leave_dict_rate=dict()
    for k in karuiList:
        decrease_leave_dict_rate[k]=[]
    decrease_leave_dict=copy.deepcopy(decrease_leave_dict_rate)
    for i in range(trial):
        for k in karuiList:
            decrease_leave=(leaveKaruiAllDict["MQ"][k][i])-leaveKaruiAllDict["MR"][k][i]
            if leaveKaruiAllDict["MQ"][k][i] != 0:
                decrease_leave_dict_rate[k].append(decrease_leave/leaveKaruiAllDict["MQ"][k][i])
            else:
                decrease_leave_dict_rate[k].append(0)
            decrease_leave_dict[k].append(decrease_leave)
            
    decrease_leave_df=pd.DataFrame.from_dict(decrease_leave_dict)
    decrease_leave_df.to_csv("Result/decrease_leave.csv", encoding="utf-8-sig")
    decrease_leave__rate_df=pd.DataFrame.from_dict(decrease_leave_dict_rate)
    decrease_leave__rate_df.to_csv("Result/decrease_leave_rate.csv", encoding="utf-8-sig")
    
    for mm in ["MR", "MQ"]:
        for k in karuiList:
            leaveKaruiAllDict[mm][k].sort()
    leave_df_MR=pd.DataFrame(leaveKaruiAllDict["MR"])
    leave_df_MR.to_csv("Result/leave_MR.csv", encoding="utf-8-sig")
    leave_df_MQ=pd.DataFrame(leaveKaruiAllDict["MQ"])
    leave_df_MQ.to_csv("Result/leave_MQ.csv", encoding="utf-8-sig")
    
    
    allprocess_time=time.time()-startall
    print("プロセス全体にかかった時間は"+str(allprocess_time)+"秒です")