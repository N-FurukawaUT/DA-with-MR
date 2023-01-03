"""
Author
------
古川直季

Comment
-------
一対一DAマッチングのプログラムを組んでみました。
少々使いづらいところもありますが、input欄の変数の内容などを変えてお試しください。

Update Note
-----------
v1.1:
    生徒を出願者に、大学を受け入れ者に名称を変更。
    大学を出願者に選ぶと起こっていたバグを解消。
    下の関数実行部分がimportされるときに実行されてしまうバグの解消。
"""
import time
import copy
import pandas as pd




class Matcher_CSV():
    def __init__(self, submitcsv, acceptcsv, isDisplay=True):
        """
        Parameters
        ----------
        submitcsv : str
            応募者側csvファイル名。絶対パスを指定するか、カレントディレクトリにファイルがあれば相対パスでよい。
        acceptcsv : str
            受け入れ側csvファイル名。同じく絶対パス、相対パスで指定してください。
        isDisplay : bool
            結果の表示を細かく行うかどうかを指定するオプション引数。デフォルトは表示するようになっています。Falseに設定すればdict型で返ってきます。
        """
        submitdata, numberofPrefS, sl=self.importsubmit(submitcsv)
        acceptdata, numberofPrefA, al=self.importaccept(acceptcsv)
        #step処理用の変数を追加する。
        #まず生徒の選好辞書を作る
        dicval=[]
        for i in range(len(sl)):
            val=submitdata.loc[i][1:numberofPrefS].to_list()
            if 'nan' in val:
                val.remove('nan')
            dicval.append(val)
        sDic=dict(zip(sl,dicval))
        for i in range(len(sl)):
            temp=[]
            temp.append(dicval[i])
            temp.append(0)
            sDic[sl[i]]=temp
        #辞書を作成する。
        aval=[] #各受け入れ者の現在の受け入れ応募者。左から順番
        for i in range(len(al)):
            aval.append(None) #暫定的にどの応募者も受け入れないとしておく
        acceptdict=dict(zip(al, aval)) #acceptListをkey,avalをvalとする辞書を作成する。受け入れ者名と、今仮受け入れしている応募者の辞書。

        while True:
            cnt=0 #出願しない人間のカウンター。これが人数分の数字になっていれば仮受け入れを正式な受け入れにする。各ステップごとに0にリセットされる。
            subd={} #出願者とその出願先の受け入れ者の辞書。
            for i in range(len(sl)):
                acceptdictValues=list(acceptdict.values()) #acceptdictの値をlistにまとめる。値は各受け入れ者の仮受け入れ応募者。
                
                if sl[i] in acceptdictValues: #すでにこの応募者は受け入れ者に仮受け入れされている。
                    cnt+=1 #カウンターを一つ増やして
                    continue #処理を続行
                else: #仮受け入れされてない場合
                    #まず文字列を変数に変換する
                    submitter=sDic[sl[i]] #文字列と同名の提出者の選好リストを取り出す。
                    submit, step=self.submit(submitter) #submit[0]は選好、submit[1]は何度目の出願か、デフォルトは0
                    if submit=="dropOut":
                        cnt+=1
                    submitter[1]=step
                    subd[sl[i]]=submit #subdはkeyに応募者名、valに志望受け入れ者名
            if cnt==len(sl):
                if isDisplay==False:
                    return acceptdict
                if isDisplay==True:
                    display=self.display(acceptdict)
                    return display
            for i in subd.keys():
                aPref=acceptdata.loc[al.index(subd[i])][1:numberofPrefA].to_list()
                if 'nan' in aPref:
                    aPref.remove('nan')
                acceptance=self.accept(acceptance=acceptdict[subd[i]],aPref=aPref,submitter=i) #応募者が出願した受け入れ者の仮受け入れ応募者を決定する。
                acceptdict[subd[i]]=acceptance #返ってきた仮受け入れ応募者を辞書に反映する。


    @classmethod
    def importsubmit(self, submitcsv):
        """
        提出者側のデータを取得する

        Parameters
        ----------
        submitcsv : str
        提出者側csvデータのパス
        """
        submitdata=pd.read_csv(str(submitcsv), header=0)
        submitdata.fillna('nan', inplace=True)
        numberofSub,numberofPrefS=submitdata.shape
        sl=submitdata['submitter'].to_list()
        return submitdata, numberofPrefS, sl

    @classmethod
    def importaccept(self, acceptcsv):
        """
        受け入れ側のデータを取得する

        Parameters
        ----------
        acceptcsv : str
        受け入れ側csvデータのパス
        """
        acceptdata=pd.read_csv(str(acceptcsv), header=0)
        acceptdata.fillna('nan', inplace=True)
        numberofAcc,numberofPrefA=acceptdata.shape
        al=acceptdata['accepter'].to_list()
        return acceptdata, numberofPrefA, al

    @classmethod
    def submit(self, submitList):
        """
        提出者の出願を取得する。

        Parameters
        ----------
        submitList : list
        0番目に選好、1番目にstepの回数が入っている
        
        Returns
        -------
        submitTo : str
            応募者の出願先。"受け入れ者名"か"dropOut"(退出権を行使)かが入る。
        """
        
        submitter=submitList[0]
        step=submitList[1]
        #提出者が退出権を行使するかどうか
        if len(submitter)<step+1:
            submitTo="dropOut"
        #現在のstepで提出するべき受け入れ者を渡す。
        else:
            submitTo=submitter[step]
            step+=1 #また出願するときのためにカウンターを増やしておく
        return submitTo, step

    @classmethod
    def accept(self, acceptance, aPref, submitter):
        """
        各受け入れ者が出願した応募者を仮受け入れするかどうかを判断する。

        Parameters
        ----------
        acceptance : str
            現在受け入れている応募者。
        aPref : list
            受け入れ者の選好リスト。
        submitter : str
            新規提出者。
        
        
        Returns
        -------
        acceptance : str
            現在受け入れている応募者。
        """

        #出願応募者と保留中応募者の選好位置を取得
        if submitter not in aPref: #出願応募者が受け入れ者の選好の中にないならば
            return acceptance #今の応募者をキープする。
        else:
            submitNum=aPref.index(submitter) #出願応募者が受け入れ者の選好の中にあるならば、探して何番目かを取得する。

        if acceptance not in aPref: #受け入れている応募者が選好の中にない場合(初期値のNone,つまり誰も受け入れてないとき)
            acceptance=submitter #出願応募者が受け入れ者の選好の中にいるかつ誰も受け入れていないから、出願応募者を受け入れる。
            return acceptance
        else:
            currentNum=aPref.index(acceptance) #初期値ではないなら必ず受け入れ者の中にある選好だから、その順序を取得する。

        if submitNum<currentNum: #出願応募者のほうをより強く選好するとき
            acceptance=submitter #受け入れ応募者を現在の応募者に変える
        else: #仮受け入れ応募者をより強く選好するとき
            acceptance=acceptance #受け入れ応募者は変わらない。
        return acceptance

    @classmethod
    def display(self, acceptdict):
        acceptName=list(acceptdict.keys()) #受け入れ者の名前
        submitName=list(acceptdict.values()) #応募者の名前
        returnStr=[] #文字列返す用の配列の準備
        for i in range(len(acceptName)):
            if submitName[i]==None:
                submitName[i]="存在しない"
            returnStr.append(acceptName[i]+"の受け入れ応募者は"+str(submitName[i])+"です。")
        print(returnStr) #受け入れ者の仮受け入れを正式受け入れとして出力する。

if __name__=="__main__": #importしたときに、このif文以下を実行しないようにするための条件
    start=time.time() #開始時間を記録します。
    result=Matcher_CSV('submit.csv','accept.csv') #関数の実行例。デフォルトのinputでは学生を応募者に、大学を受け入れ者側として実行
    #result=Matcher_CSV('submit2.csv','accept2.csv') #関数の実行例。デフォルトのinputでは大学を応募者に、学生を受け入れ者側として実行
    process_time=time.time()-start #終わった時の時間から開始時間を引いて、startとこの変数の間の処理時間を算出します。
    print(result)
    print("かかった時間は"+str(process_time)+"秒です")