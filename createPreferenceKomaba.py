import pandas as pd
import numpy as np
import random
import copy
import sys
from collections import OrderedDict as od
from import_data import facultyData
sys.dont_write_bytecode = True
import time
"""
Author
------
古川直季

Comment
-------
選好を生成するためのプログラムです。プログラムはHafalirの論文
"""
valueDict={
    "l1":{"法学部":0.3,"総合社会科学":0.1},
    "l2":{"経済学部":0.3,"総合社会科学":0.1},
    "l3":{"H群（心理学）":0.3,"J群（社会学）":0.3},
    "s1":{"機械工学A（ﾃﾞｻﾞｲﾝ・ｴﾈﾙｷﾞｰ・ﾀﾞｲﾅﾐｸｽ）":0.2, "機械工学B":0.2, "航空宇宙学":0.5,"電子情報工学":0.3,"応用物理・物理工学":0.2,"計数工学・数理/ｼｽﾃﾑ情報":0.5,"システム創成B":0.2,"システム創成C":0.3,"物理学":0.5},
    "s2":{"生命化学・工学":0.1,"薬学部":0.5},
    "s3":{"医学":0.5}
    }
ninkiDict=dict()
for karui in ["l1","l2","l3","s1","s2","s3"]:
    ninkiList=list(valueDict[karui].keys())
    ninkiDict[karui]=ninkiList
karui={"l1":104,"l2":132,"l3":111,"s1":406,"s2":217,"s3":32}
submitN={"l1":417,"l2":999,"l3":978,"s1":3712,"s2":2016,"s3":36}
avgSubmit={}
for k in karui.keys():
    avgSubmit[k]=submitN[k]/karui[k]
class CreatePrefKomaba():
    def __init__(self,karui, minorityReserveB, minorityReserveDA,alpha,theta, M, alist, slist, n, mean=0, isDelta=False, isCutOff=False, valueDict=valueDict):
        self.shitei={"l1":["法学部"], "l2":["経済学部"], "l3":["文学部", "教育学部"], "s1":["工学部", "理学部","数理科学部"], "s2":["農学部","工学部","理学部","薬学部"], "s3":["医学部"]}
        minorityReserveB, minorityReserveDA, M ,shiteiDict, fac, bunri, categoryToList=facultyData.main()
        self.fac=fac
        self.shiteiDict=shiteiDict
        self.karui=karui
        self.minorityReserveB=minorityReserveB
        self.minorityReserveDA=minorityReserveDA
        self.alpha=alpha
        self.theta=theta
        self.M=M
        self.alist=np.array(fac)
        self.slist=np.array(slist)
        self.mean=mean
        self.isDelta=isDelta
        self.typeList=["l1","l2","l3","s1","s2","s3"]
        self.bunri=bunri
        self.n=n
        self.isCutOff=isCutOff
        self.valueDict=valueDict
        self.avgSubmit=avgSubmit
        sys.dont_write_bytecode = True

    def main(self):
        """
        Parameters
        ----------
        slist : list
            申込者のリスト
        alist : list
            受け入れ者のリスト
        theta : float
            受け入れ者の選好の相関係数
        alpha : float
            申込者の選好の相関係数
        karui : dict
            各科類の人数(値はint)
        minorityReserve : dict
            指定科類枠の人数(値はint)
        M : dict
            受け入れ者の定員(値はint)
        mean : float
            マイノリティがマジョリティよりどれくらい効用が高いか
        isDelta : bool
            マイノリティとマジョリティで効用に差があるか
        """
#        numberofMinority=[round(len(self.slist)*i) for i in range(len(self.p))] #pと同じ並びでマイノリティの数を決める
#        isMinority=self.isMinority(numberofMinority)
        typeDic=self.setType(self.slist, self.karui) #生徒がどの科類かの辞書
        submitInTypes=CreatePrefKomaba.submitInTypes(self, typeDic) #科類別に分けた生徒のリスト
        sDict=CreatePrefKomaba.createPref(self, self.alist, self.alpha, self.slist, typeDic, True, self.fac)
        aDict=CreatePrefKomaba.createPref(self, self.slist, self.theta, self.alist, typeDic, False, self.fac)
        utilityDict=aDict["法学部"]
        udf=pd.DataFrame(list(utilityDict.items()), columns=["student","utility"])
        udf.to_csv('MultiThread/utilityDict'+str(self.n)+'.csv',  index=0, encoding='utf-8-sig')
        sData=CreatePrefKomaba.writecsvsub(self, sDict, typeDic, 'MultiThread\created_submit_komaba'+str(self.n))
        aData, aData2, aData3=CreatePrefKomaba.writecsvacc(self, aDict, self.M, self.minorityReserveB, self.minorityReserveDA, 'MultiThread\created_accept_komaba'+str(self.n))
        # if self.isCutOff==True:
        #     sData=CreatePrefKomaba.cutoff(self, self.n, sData, self.avgSubmit)
        if self.isCutOff==True:
            sData=CreatePrefKomaba.randomizePref(self, self.n, sData, self.avgSubmit)
        
        #CreatePrefKomaba.analyze(self, sData)
        return sData,aData, aData2, aData3
    
    def createPref(self, targetlist, correlation, selflist, typeDic, isSubmitter, faculty):
        """
        Parameters
        ----------
        targetlist : list
            効用を決めるためにつかわれる相手の名前リスト。申込者なら、受け入れ側、受け入れ側なら申込者のリストになる。
        selflist : list
            誰の選好を作るのかを決めるためのリスト。申込者の選好を作りたいなら申込者、受け入れ者の選好を作りたいなら受け入れ者のリストになる。
        correlation : float
            選好の相関係数
        typeDic : dict
            申込者がどの科類かを示す辞書(値はstr)
        isSubmitter : bool
            申し込み者側の選好か否か、Trueなら申込者の、Falseなら受け入れ者側の選好を生成する。
        """
        if isSubmitter==False: #受け入れ者側の選好
            overallspref=np.random.normal(loc=75, scale=5, size=len(targetlist))
            Prefdict={}
            for i in range(len(selflist)):
                randomizereturn=self.randomize(targetlist)
                iPrefdictvalue=(correlation*overallspref)+((1-correlation)*randomizereturn)
                iPrefdict=dict(zip(targetlist, iPrefdictvalue))
                iPrefdict = sorted(iPrefdict.items(), key=lambda x:x[1], reverse=True)
                iPrefdict=od(iPrefdict)
                Prefdict[selflist[i]]=iPrefdict
        else: #申込者側の選好
            bunkei=self.bunri["文系"]
            rikei=self.bunri["理系"]
            lmean=0
            smean=0
            Prefdict={}
            for student in selflist:
                iType=typeDic[student]
                iPrefValue=np.random.normal(loc=0, scale=2, size=78)
                iPrefdict=dict(zip(faculty, iPrefValue))
                iValueDict=self.valueDict[iType]
                for f in faculty:
                    iPrefdict[f]+=iValueDict[f]
                iPrefdict1 = sorted(iPrefdict.items(), key=lambda x:x[1], reverse=True)
                iPrefdict2 = od()
                for fac, value in iPrefdict1:
                    if value>=0:
                        iPrefdict2[fac]=value
                Prefdict[student]=iPrefdict2
        return Prefdict

    def randomize(self, targetlist):
        """
        Parameters
        ----------
        targetlist : list
            効用を決めるためにつかわれる相手の名前リスト。申込者なら、受け入れ側、受け入れ側なら申込者のリストになる。
        """
        returnlist=np.random.normal(loc=0, scale=1, size=len(targetlist))
        # if mean!=0:
        #     numberofMinority=round(len(self.slist)*self.p)
        #     minorityPref=np.random.normal(loc=mean, scale=1, size=numberofMinority)
        #     cnt=0

        #     for i in range(len(isMinority)):
        #         if isMinority[i] == True:
        #             returnlist[i]=minorityPref[cnt]
        #             cnt+=1
        #         else:
        #             continue
        return returnlist


    def writecsvsub(self, sDict, karui, filename):
        """
        Parameters
        ----------
        sDict : dict
            申込者の名前と、受け入れ者に対する選好の辞書
        isMinority : bool
            申込者がマイノリティかどうか。マイノリティならTrue、マジョリティならFalseになる。申込者全体のリストと順番が一致している。(例えば、s1,s2,s3のうち、s2がマイノリティなら[False, True, False]となる。)
        filename : str
            ファイルの名前。.csvは自動でつけるようにしているのでつけなくてもよい。
        """
        sDataframe=[]
        sDataframe.append(['submitter','karui','Preference'])
        sDicval=list(sDict.values())
        for i in range(len(self.slist)):
            temp=[]
            temp.append(self.slist[i])
            temp.append(karui[self.slist[i]])
            sDickeys=list(sDict[self.slist[i]].keys())
            for j in sDickeys:
                temp.append(j)
            sDataframe.append(temp)
        sData=pd.DataFrame(sDataframe)
        sData.to_csv(str(filename)+'.csv', header=0, index=0, encoding='utf-8-sig')
        return sData

    def writecsvacc(self, aDict, M, minorityReserveB, minorityReserveDA, filename):
        """
        Parameters
        ----------
        aDict : dict
            受け入れ者の名前と、申込者に対する選好の辞書
        M : int
            受け入れ者の定員
        filename : str
            ファイルの名前。.csvは自動でつけるようにしているのでつけなくてもよい。
        """
        aDataframe=[]
        aDataframe2=[]
        aDataframe3=[]
        aDataframe.append(['accepter','firstCapacity', 'secondCapacity','Preference'])
        aDataframe2.append(['accepter','minorityReserve'])
        aDataframe3.append(['accepter','minorityReserve'])
        aDicval=list(aDict.values())
        for i in range(len(self.alist)):
            temp=[]
            temp2=[]
            temp3=[]
            temp.append(self.alist[i])
            temp2.append(self.alist[i])
            temp3.append(self.alist[i])
            temp.append(M[self.alist[i]]["first"])
            temp.append(M[self.alist[i]]["second"])
            reserveDictB=minorityReserveB[self.alist[i]]
            for k in list(reserveDictB.keys()):
                temp2.append(k)
                temp2.append(reserveDictB[k])
            reserveDictDA=minorityReserveDA[self.alist[i]]
            for k in list(reserveDictDA.keys()):
                temp3.append(k)
                temp3.append(reserveDictDA[k])
            for j in list(aDicval[i].keys()):
                temp.append(j)
            aDataframe.append(temp)
            aDataframe2.append(temp2)
            aDataframe3.append(temp3)
        aData=pd.DataFrame(aDataframe)
        aData.to_csv(str(filename)+'.csv', header=0, index=0, encoding='utf-8-sig')
        aData2=pd.DataFrame(aDataframe2)
        aData2.to_csv(str(filename)+'MinorityReserveB.csv', header=0, index=0, encoding='utf-8-sig')
        aData3=pd.DataFrame(aDataframe3)
        aData3.to_csv(str(filename)+'MinorityReserveDA.csv', header=0, index=0, encoding='utf-8-sig')
        return aData, aData2, aData3
    
    def setType(self, slist, karui):
        tempList=[]
        karuiList=list(karui.keys())
        for i in range(len(karui)):
            tempList+=[karuiList[i]]*karui[karuiList[i]]
        typeList=tempList
        random.shuffle(typeList)
        typeDic=od(zip(slist, typeList))
        return typeDic

    def submitInTypes(self, typeDic):
        typeList=["l1","l2","l3","s1","s2","s3"]
        submitInType=dict()
        for i in typeList:
            temp=[k for k,v in typeDic.items() if v==i]
            submitInType[i]=temp
        return submitInType

    def analyze(self, sData):
        sData=sData.iloc[1:,:]
        columns=["submitter","karui"]
        for i in range(78):
            columns.append("Preference"+str(i+1))
        sData.columns=columns
        print(sData)
        for karui in ["l1","l2","l3","s1","s2","s3"]:
            Students=sData[sData["karui"]==karui]
            print(Students["Preference1"])

    def cutoff(self, n, submitDF, avgSubmit):
        #submitDF=pd.read_csv('MultiThread\created_submit_komaba'+str(n)+'.csv', header=0)
        submitCODF=[]
        tmp=["submitter","karui"]
        # tmp2=[f"Preference{i}" for i in range(1,15)]
        # tmp.extend(tmp2)
        submitCODF.append(tmp)
        submitDF=submitDF.iloc[1:,:]
        submitDF=pd.read_csv(r'MultiThread\created_submit_komaba'+str(n)+'.csv', header=0)
        for i in range(1002):
            karui=submitDF.iat[i,1]
            avg=avgSubmit[karui]
            cutoffN=round(np.random.normal(avg, avg/10, 1)[0])
            submitterPreference=submitDF.iloc[i,:cutoffN+2].to_list()
            # submitterKarui=karui
            # submitterNinki=ninkiDict[submitterKarui]
            # if list(set(submitterNinki)&set(submitterPreference))==[]:
            #     numeratorList=list(valueDict[submitterKarui].values())
            #     denominator=sum(numeratorList)
            #     numeratorList=np.array(numeratorList)
            #     probabilityList=numeratorList/denominator
            #     hoken=np.random.choice(submitterNinki, p=probabilityList)
            #     submitterPreference[6]=hoken
            if karui == "l1" or karui == "l2" or karui == "s3":
                preference=submitterPreference[2:]
                prefDict=od(zip(preference, range(len(preference)+1, 1, -1)))
                correct=np.random.normal(loc=0, scale=1, size=len(preference))
                for j in range(len(preference)):
                    prefDict[preference[j]]+=correct[j]
                prefDict = sorted(prefDict.items(), key=lambda x:x[1], reverse=True)
                newPref=[]
                for _ in prefDict:
                    newPref.append(_[0])
                submitterPreference[2:]=newPref
            submitCODF.append(submitterPreference)
        submitNewDF=pd.DataFrame(submitCODF)
        # time.sleep(0.2)
        submitNewDF.to_csv(r'MultiThread\created_submit_komaba_cutoff'+str(n)+'.csv', header=0, index=0, encoding="utf-8-sig")
        return submitNewDF
    
    def cutoff2(self, n, submitDF, avgSubmit):
        #submitDF=pd.read_csv('MultiThread\created_submit_komaba'+str(n)+'.csv', header=0)
        submitCODF=[]
        tmp=["submitter","karui"]
        # tmp2=[f"Preference{i}" for i in range(1,15)]
        # tmp.extend(tmp2)
        submitCODF.append(tmp)
        submitDF=submitDF.iloc[1:,:]
        submitDF=pd.read_csv(r'MultiThread\created_submit_komaba'+str(n)+'.csv', header=0)
        for i in range(1002):
            karui=submitDF.iat[i,1]
            avg=avgSubmit[karui]
            cutoffN=round(np.random.normal(avg, avg/10, 1)[0])
            submitterPreference=submitDF.iloc[i,:cutoffN+2].to_list()
            submitCODF.append(submitterPreference)
        submitNewDF=pd.DataFrame(submitCODF)
        # time.sleep(0.2)
        submitNewDF.to_csv(r'MultiThread\created_submit_komaba_cutoff'+str(n)+'.csv', header=0, index=0, encoding="utf-8-sig")
        return submitNewDF
            
    def randomizePref(self, n, submitDF, avgSubmit):
        #submitDF=pd.read_csv('MultiThread\created_submit_komaba'+str(n)+'.csv', header=0)
        submitCODF=[]
        tmp=["submitter","karui"]
        # tmp2=[f"Preference{i}" for i in range(1,15)]
        # tmp.extend(tmp2)
        submitCODF.append(tmp)
        submitDF=submitDF.iloc[1:,:]
        submitDF=pd.read_csv(r'MultiThread\created_submit_komaba'+str(n)+'.csv', header=0)
        for i in range(1002):
            karui=submitDF.iat[i,1]
            submitterPreference=submitDF.iloc[i,:].to_list()
            # submitterKarui=karui
            # submitterNinki=ninkiDict[submitterKarui]
            # if list(set(submitterNinki)&set(submitterPreference))==[]:
            #     numeratorList=list(valueDict[submitterKarui].values())
            #     denominator=sum(numeratorList)
            #     numeratorList=np.array(numeratorList)
            #     probabilityList=numeratorList/denominator
            #     hoken=np.random.choice(submitterNinki, p=probabilityList)
            #     submitterPreference[6]=hoken
            if karui == "l1" or karui == "l2":
                preference=submitterPreference[2:]
                prefDict=od(zip(preference, range(len(preference)+1, 1, -1)))
                correct=np.random.normal(loc=0, scale=1, size=len(preference))
                for j in range(len(preference)):
                    prefDict[preference[j]]+=correct[j]
                prefDict = sorted(prefDict.items(), key=lambda x:x[1], reverse=True)
                newPref=[]
                for _ in prefDict:
                    newPref.append(_[0])
                submitterPreference[2:]=newPref
            submitCODF.append(submitterPreference)
        submitNewDF=pd.DataFrame(submitCODF)
        # time.sleep(0.2)
        submitNewDF.to_csv(r'MultiThread\created_submit_komaba'+str(n)+'.csv', header=0, index=0, encoding="utf-8-sig")
        return submitNewDF

if __name__=="__main__":
    start=time.time() #開始時間を記録します。
    submitter=[]
    accepter=[]
    for i in range(1002):
        submitter.append("student"+str(i+1))
    accepter=["法学部", "経済学部", "文学部", "教育学部", "工学部", "理学部" ,"農学部", "医学部", "数理科学部","薬学部"]
    karui={"l1":104,"l2":132,"l3":111,"s1":406,"s2":217,"s3":32}
    alpha=0.8
    theta=1
    minorityReserveB, minorityReserveDA, M ,shiteiDict, fac, bunri, categoryToList=facultyData.main()
    karuiValueDict=dict(zip(fac,[0 for _ in range(len(fac))]))
    valueDict=dict(zip(list(karui.keys()), [copy.deepcopy(karuiValueDict) for _ in range(6)]))
    sData,aData, aData2, aData3=CreatePrefKomaba(karui, minorityReserveB,minorityReserveDA,alpha,theta, M, accepter,submitter,0 , mean=0, isDelta=False,valueDict=valueDict, isCutOff=True).main()
    print(sData,'\n', aData, '\n', aData2)
    process_time=time.time()-start #終わった時の時間から開始時間を引いて、startとこの変数の間の処理時間を算出します。
    print("かかった時間は"+str(process_time)+"秒です")