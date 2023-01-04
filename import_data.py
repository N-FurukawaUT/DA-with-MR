import pandas as pd
from collections import OrderedDict as od


class facultyData():
    def main():
        data = pd.read_csv("2019ローデータ.csv", encoding="utf-8-sig")
        data2 = data.iloc[1:79, 0:10]
        first1 = data2["第1段階指定1科類"]
        first1.fillna(999, inplace=True)
        first1 = first1.astype("int32")
        first1 = first1.astype("str")
        first1 = first1.astype("category")

        f1waku = data2["第1段階指定1枠数"]
        f1waku.fillna(999, inplace=True)
        f1waku = f1waku.astype("int32")

        first2 = data2["第1段階指定2科類"]
        first2.fillna(999, inplace=True)
        first2 = first2.astype("int32")
        first2 = first2.astype("str")
        first2 = first2.astype("category")

        f2waku = data2["第1段階指定2枠数"]
        f2waku.fillna(999, inplace=True)
        f2waku = f2waku.astype("int32")

        first3 = data2["第1段階指定3科類"]
        first3.fillna(999, inplace=True)
        first3 = first3.astype("int32")
        first3 = first3.astype("str")
        first3 = first3.astype("category")

        f3waku = data2["第1段階指定3枠数"]
        f3waku.fillna(999, inplace=True)
        f3waku = f3waku.astype("int32")

        f1KaruiDict = od(zip(data2["学科2"], first1))
        f2KaruiDict = od(zip(data2["学科2"], first2))
        f3KaruiDict = od(zip(data2["学科2"], first3))

        f1wakuDict = od(zip(data2["学科2"], f1waku))
        f2wakuDict = od(zip(data2["学科2"], f2waku))
        f3wakuDict = od(zip(data2["学科2"], f3waku))

        first1List = first1.to_list()
        first2List = first2.to_list()
        first3List = first3.to_list()
        karuiDict = {"1": "l1", "2": "l2", "3": "l3",
                     "4": "s1", "5": "s2", "6": "s3"}
        karuiList = list(set(first1List+first2List+first3List))
        karuiListValue = []
        for i in range(len(karuiList)):
            karuiListValue.append([])
        for i in range(len(karuiList)):
            temp = karuiList[i]
            temp2 = karuiListValue[i]
            for j in karuiDict.keys():
                if j in temp:
                    temp2.append(karuiDict[j])
        categoryToList = dict(zip(karuiList, karuiListValue))
        fKaruiDictList = [f1KaruiDict, f2KaruiDict, f3KaruiDict]
        fWakuDictList = [f1wakuDict, f2wakuDict, f3wakuDict]
        data3 = data.loc[1:79, "第二段階指定1科類":"第二段階指定4枠数"]

        second1 = data3["第二段階指定1科類"]
        second1.fillna(999, inplace=True)
        second1 = second1.astype("int32")
        second1 = second1.astype("str")

        s1waku = data3["第二段階指定1枠数"]
        s1waku.fillna(999, inplace=True)
        s1waku = s1waku.astype("int32")

        second2 = data3["第二段階指定2科類"]
        second2.fillna(999, inplace=True)
        second2 = second2.astype("int32")
        second2 = second2.astype("str")

        s2waku = data3["第二段階指定2枠数"]
        s2waku.fillna(999, inplace=True)
        s2waku = s2waku.astype("int32")

        second3 = data3["第二段階指定3科類"]
        second3.fillna(999, inplace=True)
        second3 = second3.astype("int32")
        second3 = second3.astype("str")

        s3waku = data3["第二段階指定3枠数"]
        s3waku.fillna(999, inplace=True)
        s3waku = s3waku.astype("int32")

        second4 = data3["第二段階指定4科類"]
        second4.fillna(999, inplace=True)
        second4 = second4.astype("int32")
        second4 = second4.astype("str")

        s4waku = data3["第二段階指定4枠数"]
        s4waku.fillna(999, inplace=True)
        s4waku = s4waku.astype("int32")

        s1KaruiDict = od(zip(data2["学科2"], second1))
        s2KaruiDict = od(zip(data2["学科2"], second2))
        s3KaruiDict = od(zip(data2["学科2"], second3))
        s4KaruiDict = od(zip(data2["学科2"], second4))

        s1wakuDict = od(zip(data2["学科2"], s1waku))
        s2wakuDict = od(zip(data2["学科2"], s2waku))
        s3wakuDict = od(zip(data2["学科2"], s3waku))
        s4wakuDict = od(zip(data2["学科2"], s4waku))

        second1List = second1.to_list()
        second2List = second2.to_list()
        second3List = second3.to_list()
        karuiDict = {"1": "l1", "2": "l2", "3": "l3",
                     "4": "s1", "5": "s2", "6": "s3"}
        karuiList = list(set(second1List+second2List+second3List))
        karuiListValue = []
        for i in range(len(karuiList)):
            karuiListValue.append([])
        for i in range(len(karuiList)):
            temp = karuiList[i]
            temp2 = karuiListValue[i]
            for j in karuiDict.keys():
                if j in temp:
                    temp2.append(karuiDict[j])
        categoryToList = dict(zip(karuiList, karuiListValue))

        sKaruiDictList = [s1KaruiDict, s2KaruiDict, s3KaruiDict]
        sWakuDictList = [s1wakuDict, s2wakuDict, s3wakuDict]
        fac = data2["学科2"].to_list()
        minorityReserveB = od()
        minorityReserveDA = od()
        M = od()
        for i in fac:
            tempDict = dict()
            tempValueB = 0
            tempValueDA = 0
            if f1KaruiDict[i] == "999" or f1wakuDict[i] == 999:
                pass
            else:
                tempDict[f1KaruiDict[i]] = f1wakuDict[i]
                tempValueB += f1wakuDict[i]
            if f2KaruiDict[i] == "999" or f2wakuDict[i] == 999:
                pass
            else:
                tempDict[f2KaruiDict[i]] = f2wakuDict[i]
                tempValueB += f2wakuDict[i]
            if f3KaruiDict[i] == "999" or f3wakuDict[i] == 999:
                pass
            else:
                tempValueB += f3wakuDict[i]
            minorityReserveB[i] = tempDict
            tempDict2 = dict()
            if s1KaruiDict[i] == "999" or s1wakuDict[i] == 999:
                pass
            else:
                tempDict2[s1KaruiDict[i]] = s1wakuDict[i]
                tempValueDA += s1wakuDict[i]
            if s2KaruiDict[i] == "999" or s2wakuDict[i] == 999:
                pass
            else:
                tempDict2[s2KaruiDict[i]] = s2wakuDict[i]
                tempValueDA += s2wakuDict[i]
            if s3KaruiDict[i] == "999" or s3wakuDict[i] == 999:
                pass
            else:
                tempDict2[s3KaruiDict[i]] = s3wakuDict[i]
                tempValueDA += s3wakuDict[i]
            if s4KaruiDict[i] == "999" or s4wakuDict[i] == 999:
                pass
            else:
                tempDict2[s4KaruiDict[i]] = s4wakuDict[i]
                tempValueDA += s4wakuDict[i]
            minorityReserveDA[i] = tempDict2
            tempValueDict = dict()
            tempValueDict["first"] = tempValueB
            tempValueDict["second"] = tempValueDA
            M[i] = tempValueDict
        #指定科類枠の設定
        shiteiDict=dict()
        for type in ["l1","l2","l3","s1","s2","s3"]:
            category=[k for k,v in categoryToList.items() if type in v]
            shiteiFaculty=[k for k,v in s1KaruiDict.items() if v in category]
            shiteiDict[type]=shiteiFaculty
        bunkei=data2.iloc[0:17,3].to_list()
        rikei=data2.iloc[17:20,3].to_list()+data2.iloc[31:79,3].to_list()
        kyoyo=data2.iloc[20:31,3].to_list()
        bunri={"文系":bunkei,"理系":rikei,"教養":kyoyo}
        return minorityReserveB, minorityReserveDA, M, shiteiDict, fac, bunri, categoryToList


minorityReserveB, minorityReserveDA, M, shiteiDict, fac, bunri, categoryToList=facultyData.main()
print(M)