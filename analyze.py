import pandas as pd
import numpy as np
from import_data import facultyData
class analyze(object):
    def __init__(self, submitname, mirResultname, MaqResultname, accepter,n):
        """
        Parameters
        ----------
        submitname : str
            応募者側csvファイル名。絶対パスを指定するか、カレントディレクトリにファイルがあれば相対パスでよい。
        mirResultname : str
            DA with minority reserveの結果csvファイル名。同じく絶対パス、相対パスで指定してください。
        MaqResultname : str
            DA with Majority quotaの結果csvファイル名。同じく絶対パス、相対パスで指定してください。
        """
        minorityReserveB, minorityReserveDA, M ,shiteiDict, fac, bunri, categoryToList=facultyData.main()
        submit=pd.read_csv(submitname, header=0)
        accept=pd.read_csv(accepter, header=0)
        al=accept["accepter"].to_list()
        sl=submit['submitter'].to_list()
        karui=submit['karui'].to_list()
        karuiDict=dict(zip(sl, karui))
        
        
        minorityDict=dict()
        minorityReserveDA_sorted=dict()
        for f in fac:
            minorityReserveDA_sorted[f]=sorted(minorityReserveDA[f].items(), key=lambda x:x[1], reverse=True)
            categoryToList["123456"]=[]
        for f in fac:
            tmp=[]
            for _ in range(len(minorityReserveDA_sorted[f])):
                if (len(minorityReserveDA_sorted[f][_][0]) != 6):
                    value=minorityReserveDA_sorted[f][_][0]
                    if (categoryToList[value]!=[]) and (minorityReserveDA_sorted[f][_][1]!=0):
                        tmp=tmp+categoryToList[value]
            minorityDict[f]=tmp
        
        
        # minorityDict=dict()
        # minorityReserveDA_sorted=dict()
        # for f in fac:
        #     minorityReserveDA_sorted[f]=sorted(minorityReserveDA[f].items(), key=lambda x:x[1], reverse=True)
        #     categoryToList["123456"]=[]
        # for f in fac:
        #     flag=True
        #     for _ in range(len(minorityReserveDA_sorted[f])):
        #         if (len(minorityReserveDA_sorted[f][_][0]) != 6) and (flag==True):
        #             value=minorityReserveDA_sorted[f][_][0]
        #             minorityDict[f]=categoryToList[value]
        #             if (minorityReserveDA_sorted[f][_][1] != 0):
        #                 flag=False
        #     if flag==True:
        #         minorityDict[f]=[]
                
                
        self.minorityDict = minorityDict
        numberofSub,numberofPrefS=submit.shape
        Pref=[]
        for i in range(len(sl)):
            val=submit.loc[i][2:numberofPrefS].to_list()
            val=[s for s in val if s!= 'nan']
            Pref.append(val)
        self.sl=sl
        self.al=al
        self.mirResultname=mirResultname
        self.MaqResultname=MaqResultname
        self.Pref=Pref
        self.karui=karui
        self.karuiDict=karuiDict
        self.n=n
        self.fac=fac
        self.M=M

    def main(self):
        fixedsPairmir=self.minorityReserve(self.sl, self.mirResultname)
        fixedsPairMaq=self.MajorityQuota(self.sl,self.MaqResultname)
        betterWorseDict, mirCount, maqCount, leaveKaruiDict=self.compare(self.sl, fixedsPairmir, fixedsPairMaq, self.Pref, self.karui, self.karuiDict, self.al)
        # utilityMinusDict=self.compareFac(self.mirResultname, self.MaqResultname, self.n)
        utilityMinusDict=self.compareFac2(self.n)
        dfFRmir=self.mirFillRate(self.mirResultname)
        dfFRMaq=self.MaqFillRate(self.MaqResultname)
        return betterWorseDict, utilityMinusDict, mirCount, maqCount, leaveKaruiDict, dfFRmir, dfFRMaq
####minority reserve
    def minorityReserve(self, sl, mirResultname):
        submitresultmir=pd.read_csv(mirResultname, header=0)
        numberofAcceptmir, numberofSubmitmir=submitresultmir.shape
        submitresultmir.fillna('nan', inplace=True)
        alistmir=submitresultmir['accepter'].to_list()
        sPairmir=[]
        for i in range(len(alistmir)):
            val=submitresultmir.loc[i][0:numberofSubmitmir].to_list()
            val=[s for s in val if s!= 'nan'] 
            for j in range(1,len(val)):
                temp=[]
                temp.append(val[j])
                temp.append(val[0])
                sPairmir.append(temp)
            submitterlistmir=[]
        for i in sPairmir:
            submitterlistmir.append(i[0])
        for i in sl:
            if i not in submitterlistmir:
                submitterlistmir.append(i)
                sPairmir.append([i,'leave'])
        fixedsPairmir=[]
        for i in sl:
            number=submitterlistmir.index(i)
            fixedsPairmir.append(sPairmir[number])
        return fixedsPairmir
####################
####majority quota
    def MajorityQuota(self, sl,MaqResultname):
        submitresultMaq=pd.read_csv(MaqResultname, header=0)
        numberofAcceptMaq, numberofSubmitMaq=submitresultMaq.shape
        submitresultMaq.fillna('nan', inplace=True)
        alistMaq=submitresultMaq['accepter'].to_list()
        sPairMaq=[]
        for i in range(len(alistMaq)):
            val=submitresultMaq.loc[i][0:numberofSubmitMaq].to_list()
            val=[s for s in val if s!= 'nan'] 
            for j in range(1, len(val)):
                temp=[]
                temp.append(val[j])
                temp.append(val[0])
                sPairMaq.append(temp)
        submitterlistMaq=[]
        for i in sPairMaq:
            submitterlistMaq.append(i[0])
        for i in sl:
            if i not in submitterlistMaq:
                submitterlistMaq.append(i)
                sPairMaq.append([i, 'leave'])
        fixedsPairMaq=[]
        for i in sl:
            number=submitterlistMaq.index(i)
            fixedsPairMaq.append(sPairMaq[number])
        return fixedsPairMaq
##################
####compare
    def compare(self, sl, fixedsPairmir, fixedsPairMaq, Pref, karui, karuiDict, al):
        compareResult=[] #minority reserveがmajorityquotaに対して悪くなっていれば-1 変わらなければ0 良くなっていれば1が入る
        compareIndex=[["student","mirIndex","MaqIndex"]]
        mirCount=0
        maqCount=0
        leaveKaruiDict={"l1":[0,0],"l2":[0,0],"l3":[0,0],"s1":[0,0],"s2":[0,0],"s3":[0,0]}
        for i in range(len(sl)):
            mirResult=fixedsPairmir[i][1]
            MaqResult=fixedsPairMaq[i][1]
            isLeavemir=False
            isLeaveMaq=False
            if mirResult=='leave':
                mirResultindex=len(Pref[i])+1
                isLeavemir=True
                leaveKaruiDict[karuiDict[sl[i]]][0]+=1
                mirCount+=1
            if MaqResult=='leave':
                MaqResultindex=len(Pref[i])+1
                isLeaveMaq=True
                leaveKaruiDict[karuiDict[sl[i]]][1]+=1
                maqCount+=1
            if isLeavemir==False:
                mirResultindex=Pref[i].index(mirResult)#選好の何番目かを取得
            if isLeaveMaq==False:
                MaqResultindex=Pref[i].index(MaqResult)
            #print(mirResultindex, MaqResultindex, str(i)+"step")
            #mirの結果をMaqより選好すれば1,逆なら-1、変わらなければ0
            if mirResultindex<MaqResultindex:
                compareResult.append([sl[i],1,isLeavemir,isLeaveMaq])
            elif mirResultindex==MaqResultindex:
                compareResult.append([sl[i],0,isLeavemir,isLeaveMaq])
            elif mirResultindex>MaqResultindex:
                compareResult.append([sl[i],-1,isLeavemir,isLeaveMaq])
            compareIndex.append([sl[i],mirResultindex,MaqResultindex])
        karuiList=["l1", "l2", "l3", "s1", "s2", "s3"]
        #karuiResultdict=dict(zip(karuiList, []*len(karuiList)))
        karuiResultdict=dict()
        for i in karuiList:
            karuiResultdict[i]=[]
        #betterWorseDict=dict(zip(karuiList, []*len(karuiList)))
        betterWorseDict=dict()
        for i in karuiList:
            betterWorseDict[i]=[]
        for i in range(len(sl)):
            submit=sl[i]
            slkarui=karuiDict[submit]
            karuiResult=karuiResultdict[slkarui]
            karuiResult.append(compareResult[i][1])
        for type in karuiList:
            karuiCompareResult=karuiResultdict[type]
            karuiBetter=karuiCompareResult.count(1)
            karuiWorse=karuiCompareResult.count(-1)
            betterWorse=betterWorseDict[type]
            betterWorse.append(karuiBetter)
            betterWorse.append(karuiWorse)
        compareResult.append(["合計","",mirCount,maqCount])
        compareResult.insert(0,['submitter','result',"isLeavemir","isLeaveMaq"])
        comparedata=pd.DataFrame(compareResult)
        comparedata.to_csv('MultiThread/CompareResult'+str(self.n)+'.csv',header=0, index=0, encoding='utf-8-sig')
        compareIndexData=pd.DataFrame(compareIndex)
        compareIndexData.to_csv("MultiThread/CompareIndex"+str(self.n)+".csv",header=0, index=0, encoding="utf-8-sig")
        return betterWorseDict, mirCount, maqCount, leaveKaruiDict
###########
####compare faculity
    def compareFac(self, mirResultname, MaqResultname, n):
        submitresultmir=pd.read_csv(mirResultname, header=0, index_col=0)
        submitresultMaq=pd.read_csv(MaqResultname, header=0, index_col=0)
        utilityDict=pd.read_csv("MultiThread/utilityDict"+str(n)+".csv", header=0)
        #utilityDict=utilityDict.to_dict()
        utilityDict=dict(zip(utilityDict.iloc[:,0].to_list(),utilityDict.iloc[:,1].to_list()))
        facList=submitresultmir.index.values.tolist()
        facUtility=[]
        facUtility.append(["faculty","UtilityOfmir(shitei)","UtilityOfmir(other)","UtilityOfMaq(shitei)","UtilityOfMaq(other)"])
        utilityMinusDict=dict()
        for fac in facList:
            facStudentmir=submitresultmir.loc[fac]
            facStudentmir=facStudentmir.fillna("nan")
            facStudentmir=facStudentmir.tolist()
            utilitySummirShitei=0
            utilitySummirOther=0
            for student in facStudentmir:
                if student!="nan":
                    if self.karuiDict[student] in self.minorityDict[fac]:
                        utilitySummirShitei+=utilityDict[student]
                    else:
                        utilitySummirOther+=utilityDict[student]
            facStudentMaq=submitresultMaq.loc[fac]
            facStudentMaq=facStudentMaq.fillna("nan")
            facStudentMaq=facStudentMaq.tolist()
            utilitySumMaqShitei=0
            utilitySumMaqOther=0
            for student in facStudentMaq:
                if student!="nan":
                    if self.karuiDict[student] in self.minorityDict[fac]:
                        utilitySumMaqShitei+=utilityDict[student]
                    else:
                        utilitySumMaqOther+=utilityDict[student]
            facUtility.append([fac,utilitySummirShitei,utilitySummirOther,utilitySumMaqShitei,utilitySumMaqOther])
            utilityMinusShitei=utilitySummirShitei-utilitySumMaqShitei
            utilityMinusOther=utilitySummirOther-utilitySumMaqOther
            utilityMinus=utilityMinusShitei+utilityMinusOther
            utilityMinusDict[fac]=np.array([utilityMinusShitei, utilityMinusOther, utilityMinus])
        facdf=pd.DataFrame(facUtility)
        facdf.to_csv("MultiThread/FacultyUtility"+str(n)+".csv", header=0, index=0, encoding='utf-8-sig')
        return utilityMinusDict
    
    def compareFac2(self, n):
        MQ_mir=pd.read_csv(f"MultiThread/minority_acceptance_MQ{n}.csv",header=None , index_col=0)
        MQ_maj=pd.read_csv(f"MultiThread/majority_acceptance_MQ{n}.csv",header=None , index_col=0)
        MR_mir=pd.read_csv(f"MultiThread/minority_acceptance_MR{n}.csv",header=None , index_col=0)
        MR_maj=pd.read_csv(f"MultiThread/majority_acceptance_MR{n}.csv",header=None , index_col=0)
        utilityDict=pd.read_csv("MultiThread/utilityDict"+str(n)+".csv", header=0)
        #utilityDict=utilityDict.to_dict()
        utilityDict=dict(zip(utilityDict.iloc[:,0].to_list(),utilityDict.iloc[:,1].to_list()))
        facList=MQ_mir.index.values.tolist()
        facUtility=[]
        facUtility.append(["faculty","UtilityOfMaq(shitei)","UtilityOfMaq(other)", "UtilityOfmir(shitei)","UtilityOfmir(other)"])
        utilityMinusDict=dict()
        for fac in facList:
            utilitySumMaqShitei=0
            utilitySumMaqOther=0
            utilitySummirShitei=0
            utilitySummirOther=0 
            data_list=[MQ_mir, MQ_maj, MR_mir, MR_maj]
            init_list=[utilitySumMaqShitei,utilitySumMaqOther,utilitySummirShitei,utilitySummirOther]
            temp=[]
            for i in range(4):
                data=data_list[i]
                init=init_list[i]
                fac_student=data.loc[fac, :].dropna().to_list()
                for student in fac_student:
                    init += utilityDict[student]
                temp.append(init)
                init_list[i]=init
            facUtility.append([fac]+temp)
            # utilityMinusShitei=utilitySummirShitei-utilitySumMaqShitei
            # utilityMinusOther=utilitySummirOther-utilitySumMaqOther
            utilityMinusShitei=init_list[2]-init_list[0]
            utilityMinusOther=init_list[3]-init_list[1]
            utilityMinus=utilityMinusShitei+utilityMinusOther
            utilityMinusDict[fac]=np.array([utilityMinusShitei, utilityMinusOther, utilityMinus])
        facdf=pd.DataFrame(facUtility)
        facdf.to_csv("MultiThread/FacultyUtility"+str(n)+".csv", header=0, index=0, encoding='utf-8-sig')
        return utilityMinusDict
        
####mir fill rate
    def  mirFillRate(self, mirResultname):
        submitresultmir=pd.read_csv(mirResultname, header=0, index_col=0)
        fillRatemir=list()
        for f in self.fac:
            facSeries=submitresultmir.loc[f,:].dropna()
            length=len(facSeries)
            fillRatemir.append([f, length/self.M[f]["second"]])
        dfFRmir=pd.DataFrame(fillRatemir, columns=["faculty", "fill rate"])
        dfFRmir.to_csv(f"MultiThread/fill_rate_mir{self.n}.csv", encoding="utf-8-sig", index=0)
        return dfFRmir
####Maq fill rate
    def  MaqFillRate(self, MaqResultname):
        submitresultMaq=pd.read_csv(MaqResultname, header=0, index_col=0)
        fillRateMaq=list()
        for f in self.fac:
            facSeries=submitresultMaq.loc[f,:].dropna()
            length=len(facSeries)
            fillRateMaq.append([f, length/self.M[f]["second"]])
        dfFRMaq=pd.DataFrame(fillRateMaq, columns=["faculty", "fill rate"])
        dfFRMaq.to_csv(f"MultiThread/fill_rate_Maq{self.n}.csv", encoding="utf-8-sig", index=0)
        return dfFRMaq
####################
if __name__=="__main__":
    import time
    start=time.time() #開始時間を記録します。
    betterWorseDict, utilityMinusDict, mirCount, maqCount, leaveKaruiDict, dfFRmir, dfFRMaq=analyze('MultiThread/created_submit_komaba0.csv','MultiThread/submitmirResultKomaba0.csv','MultiThread/submitMaqResultKomaba0.csv', "MultiThread/created_accept_komaba0.csv", 1).main()
    print(betterWorseDict)
    print(leaveKaruiDict)
    process_time=time.time()-start #終わった時の時間から開始時間を引いて、startとこの変数の間の処理時間を算出します。
    print("かかった時間は"+str(process_time)+"秒です")