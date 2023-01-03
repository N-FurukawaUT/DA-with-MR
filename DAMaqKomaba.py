"""
Author
------
古川直季

Comment
-------
DA with majority quotaのプログラムを組んでみました。
何か問題がありましたらslackのほうに投げていただければ修正いたします。
"""
from DA_CSV import Matcher_CSV
import pandas as pd
import time
import copy
import numpy as np
from import_data import facultyData
class DAMaqKomaba():
    def __init__(self, submitcsv, acceptcsv,n, isDisplay=False, filename='submitMaqResultKomaba'):
        """
        Parameters
        ----------
        submitcsv : str
            応募者側csvファイル名。絶対パスを指定するか、カレントディレクトリにファイルがあれば相対パスでよい。
        acceptcsv : str
            受け入れ側csvファイル名。同じく絶対パス、相対パスで指定してください。
        isDisplay : bool
            結果の表示を細かく行うかどうかを指定するオプション引数。デフォルトは表示しないようになっています。Trueに設定すれば成形された形で返ってきます。
        filename : str
            ファイル名を指定するオプション引数。デフォルトではsubmitMaqResult.csvとなります。
        """
        self.isDisplay=isDisplay
        self.filename=filename
        typeList=["l1","l2","l3","s1","s2","s3"]
        minorityReserveB, minorityReserveDA, M ,shiteiDict, fac, bunri, categoryToList=facultyData.main()
        self.categoryToList=categoryToList
        self.n=n
        DAMaqKomaba.main(self, submitcsv, acceptcsv, self.isDisplay, self.filename)
    def main(self, submitcsv, acceptcsv, isDisplay, filename):
        Matcher=Matcher_CSV
        submitdata, numberofPrefS, sl=Matcher.importsubmit(submitcsv)
        karuidic=dict(zip(sl, submitdata['karui'].to_list()))
        acceptdata, numberofPrefA, al=Matcher.importaccept(acceptcsv)
        firstCapacity=acceptdata['firstCapacity'].to_list()
        firstCapacity=dict(zip(al, firstCapacity))
        secondCapacity=acceptdata['secondCapacity'].to_list()
        secondCapacity=dict(zip(al, secondCapacity))
        MRdfB=DAMaqKomaba.importMinorityReserve(self, "MultiThread\created_accept_komaba"+str(self.n)+"MinorityReserveB.csv")
        MRdfDA=DAMaqKomaba.importMinorityReserve(self, r"2019ローデータ_枠早見表.csv")
        MRnum, MRlen=MRdfDA.shape
        MRDictDA=dict()
        for i in range(len(al)):
            tempdict=dict()
            for j in range(int((MRlen-1)/2)):
                if MRdfDA.iat[i, 2*j+1] != "nan":
                    tempdict[str(int(MRdfDA.iat[i, 2*j+1]))]=int(MRdfDA.iat[i,2*j+2])
            MRDictDA[al[i]]=tempdict
        # MRDictB=dict()
        # for i in range(len(al)):
        #     tempdict=dict()
        #     for j in range(int((MRlen-1)/2)):
        #         if MRdfB.iat[i, 2*j+1] != "nan":
        #             tempdict[str(int(MRdfB.iat[i, 2*j+1]))]=int(MRdfB.iat[i,2*j+2])
        #     MRDictB[al[i]]=tempdict
        #step処理用の変数を追加する。
        #まず辞書を作る
        sdicval=[]
        for i in range(len(sl)):
            val=submitdata.loc[i][2:numberofPrefS].to_list()
            val=[s for s in val if s!= 'nan'] 
            sdicval.append(val)
        sDic=dict(zip(sl,sdicval))
        for i in range(len(sl)):
            temp=[]
            temp.append(sdicval[i])
            temp.append(0)
            sDic[sl[i]]=temp
        adicval=[]
        for i in range(len(al)):
            val=acceptdata.loc[i][3:numberofPrefA].to_list()
            val=[s for s in val if s!= 'nan'] 
            adicval.append(val)
        aDic=dict(zip(al,adicval))
        #辞書を作成する。
        aval=[] #各受け入れ者の現在の受け入れ応募者。左から順番
        aval2=[] #各受け入れ者のマイノリティ、マジョリティ別の受け入れ応募者。左から順番
        aval3=[]
        for i in range(len(al)):
            aval.append([]) #暫定的にどの応募者も受け入れないとしておく。一対多マッチングだからリストにしておく
            aval2.append([[],[]])
            aval3.append({})
        acceptdictDA=dict(zip(al, aval)) #acceptListをkey,avalをvalとする辞書を作成する。受け入れ者名と、今仮受け入れしている応募者の辞書。
        acceptdictMm=dict(zip(al, aval2)) #acceptListをkey, aval2をvalとする辞書を作成する。valはマイノリティ、マジョリティでの受け入れ者
        acceptdictMinorityReserve=dict(zip(al, aval3))


        stepcnt=0
        while True:
            stepcnt+=1
            cnt=0 #出願しない人間のカウンター。これが人数分の数字になっていれば仮受け入れを正式な受け入れにする。各ステップごとに0にリセットされる。
            subd={} #出願者とその出願先の受け入れ者の辞書。
            
            acceptdictValues=[]
            submitterstart=time.time()
            for j in acceptdictDA.values():
                acceptdictValues+=j
            for j in acceptdictDA.values():
                acceptdictValues+=j
            acceptdictValues=set(acceptdictValues)
            for i in range(len(sl)):
#                acceptdictValues=list(acceptdict.values()) #acceptdictの値をlistにまとめる。値は各受け入れ者の仮受け入れ応募者。
                if sl[i] in acceptdictValues: #すでにこの応募者は受け入れ者に仮受け入れされている。
                    cnt+=1 #カウンターを一つ増やして
                    continue #処理を続行
                else: #仮受け入れされてない場合
                    #まず文字列を変数に変換する
                    submitter=sDic[sl[i]] #文字列と同名の提出者の選好リストを取り出す。
                    submit, step=Matcher.submit(submitter) #submit[0]は選好、submit[1]は何度目の出願か、デフォルトは0
                    if submit=="dropOut":
                        cnt+=1
                        submitter[1]=step #ステップ追加
                    else:
                        submitter[1]=step
                        if not submit in subd:
                            subd[submit]=[] #空リストを作成
                        subd[submit].append(sl[i]) #subdはkeyに受け入れ者名、valに申込者リスト
            submitterend=time.time()-submitterstart
            #print(submitterend)
            if cnt==len(sl):
                acceptdict=copy.deepcopy(acceptdictDA)
                dataframe=[]
                dataframe.append(['accepter', 'result'])
                acceptdictkeys=list(acceptdict.keys())
                acceptdictvalues=list(acceptdict.values())
                for i in range(len(acceptdictkeys)):
                    temp=[]
                    temp.append(acceptdictkeys[i])
                    dictValues=np.unique(acceptdictvalues[i])
                    for j in dictValues:
                        temp.append(j)
                    dataframe.append(temp)
                data=pd.DataFrame(dataframe)
                data.to_csv("MultiThread/"+str(filename)+'.csv', header=0, index=0, encoding='utf-8-sig')
                #マイノリティ、マジョリティ別
                acceptdict=acceptdictMm
                dataframeMinority=[]
                dataframeMajority=[]
                for a in al:
                    for mm in ["minority", "majority"]:
                        temp=[]
                        temp.append(a)
                        if mm =="minority":
                            dictValues=acceptdict[a][0]
                            temp=temp+dictValues
                            dataframeMinority.append(temp)
                        else:
                            dictValues=acceptdict[a][1]
                            temp=temp+dictValues
                            dataframeMajority.append(temp)
                dataMinority=pd.DataFrame(dataframeMinority)
                np.save(f"MultiThread/sim_fill{self.n}.npy", acceptdictMinorityReserve)
                dataMinority.to_csv(f"MultiThread/minority_acceptance_MQ{self.n}.csv", header=0, index=0, encoding='utf-8-sig')
                dataMajority=pd.DataFrame(dataframeMajority)
                dataMajority.to_csv(f"MultiThread/majority_acceptance_MQ{self.n}.csv", header=0, index=0, encoding='utf-8-sig')
                print('総ステップ数'+str(stepcnt)+'回')
                if isDisplay==False: #表示設定オフ
                    return
                if isDisplay==True: #表示設定オン
                    display=Matcher.display(acceptdict)
                    return
            else:#もし出願が終わってないなら
                for i in subd.keys(): #iは大学名
                    acceptance, minorityacceptanceDict, minorityacceptanceAll, majorityacceptance=DAMaqKomaba.accept(self, acceptdictDA[i], aDic[i], subd[i],MRDictDA[i], secondCapacity[i], karuidic, i, sl) #応募者が出願した受け入れ者の仮受け入れ応募者を決定する。
                    acceptdictDA[i]=acceptance #返ってきた仮受け入れ応募者を辞書に反映する。
                    acceptdictMm[i]=[minorityacceptanceAll, majorityacceptance]
                    acceptdictMinorityReserve[i]=minorityacceptanceDict


    def accept(self, acceptance, aPref, submitter,MRDict, capacity, karuidict, accepter,sl):
        """
        Parameters
        ----------
        acceptance : list
            受け入れ者側の仮受け入れ者リスト。
        aPref : list
            受け入れ側csvファイル名。同じく絶対パス、相対パスで指定してください。
        submitter : list
            この段階で新規に提出してきた申込者のリスト
        minorityReserve : int
            マイノリティリザーブの数
        capcity : int
            受け入れ者側の定員
        minoritylist : list
            申込者側のマイノリティが羅列されたリスト
        majoritylist : list
            申込者側のマジョリティが羅列されたリスト
        """
        for i in submitter:
            acceptance.append(i)
        aPrefminus=aPref[:]
        acceptancePref=aPref[:] #選好順位
        for i in acceptance:
            aPrefminus.remove(i)
        for i in aPrefminus:
            acceptancePref.remove(i)
        minorityDict=dict()
        minorityListAll=[]
        for category in MRDict.keys():
            if category!="123456":
                type=self.categoryToList[category]
                minorityListCategory=[]
            for karui in type:
                minoritylist=[k for k,v in karuidict.items() if v==karui]
                minorityListCategory+=minoritylist
                minorityListAll+=minoritylist
            minorityDict[category]=minorityListCategory
        majoritylist=list(set(sl)-set(minorityListAll))
        acminorityDict=dict()
        acminorityAll=[]
        for type in minorityDict.keys():
            if type!="123456":
                minoritylist=minorityDict[type]
                acminority=list(set(acceptancePref)&set(minoritylist)) #acceptanceの中のマイノリティリスト(科類別)
                acminorityDict[type]=acminority
                acminorityAll+=acminority
        acmajority=list(set(acceptancePref)&set(majoritylist)) #acceptanceの中のマイノリティリスト
        minorityacceptance=acceptancePref[:]
        majorityacceptance=acceptancePref[:]
        for i in acmajority:
            minorityacceptance.remove(i) #マイノリティ申込者(科類関係なし)の選好順序付リスト。選好が強い順
        karuiPrefDict=dict()
        minorityacceptanceDict=dict()
        for type in acminorityDict.keys():
            if type!="123456":
                ackaruiminority=minorityacceptance[:]
                karuiminority=acminorityDict[type]
                otherKaruiMinority=list(set(acminorityAll)-set(karuiminority))
                for i in otherKaruiMinority:
                    ackaruiminority.remove(i) #各科類の選好順序付きリスト
                karuiPrefDict[type]=ackaruiminority
        minorityacceptanceAll=[]
        minorityReserveAll=0
        for type in karuiPrefDict.keys():
            if type!="123456":
                minorityReserve=MRDict[type]
                minorityReserve=int(minorityReserve)
                minorityReserveAll+=minorityReserve
                minorityacceptance=karuiPrefDict[type]
                if minorityReserve<len(minorityacceptance): #マイノリティの数がマイノリティリザーブより多い
                    rejectmi=minorityacceptance[minorityReserve:len(minorityacceptance)]
                    minorityacceptance[minorityReserve:len(minorityacceptance)]=[] #枠外の申込者を排除
                    for j in rejectmi:
                        acminorityAll.remove(j) #majorityacceptance用に除いておく
                minorityacceptanceDict[type]=minorityacceptance
                minorityacceptanceAll+=minorityacceptance


        for i in acminorityAll:
            majorityacceptance.remove(i) #マジョリティ申込者の選好順序付リスト。
        if len(majorityacceptance)>capacity-minorityReserveAll: #もしマジョリティの数が残りの枠より多ければ
            majorityacceptance[capacity-minorityReserveAll:len(majorityacceptance)]=[] #オーバーした分をリストから削除
        acceptance=minorityacceptanceAll+majorityacceptance
        return acceptance, minorityacceptanceDict, minorityacceptanceAll, majorityacceptance

    def importMinorityReserve(self, filename):
        MRdf=pd.read_csv(filename, header=0)
        MRdf.fillna('nan', inplace=True)
        return MRdf

if __name__=="__main__": #importしたときに、このif文以下を実行しないようにするための条件
    start=time.time() #開始時間を記録します。
    DAMaqKomaba('MultiThread\created_submit_komaba0.csv','MultiThread\created_accept_komaba0.csv', 0, filename="submitMaqResultKomaba0") #関数の実行例。デフォルトのinputでは学生を応募者に、大学を受け入れ者側として実行
    #DAMaqKomaba('created_submit.csv','created_accept.csv')
    #result=Matcher_CSV('submit2.csv','accept2.csv') #関数の実行例。デフォルトのinputでは大学を応募者に、学生を受け入れ者側として実行
    process_time=time.time()-start #終わった時の時間から開始時間を引いて、startとこの変数の間の処理時間を算出します。
    print("かかった時間は"+str(process_time)+"秒です")