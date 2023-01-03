from createPreferenceKomabaTest import CreatePrefKomaba
from DAMaqKomaba import DAMaqKomaba
from import_data import facultyData
import pandas as pd
import numpy as np
import copy
from collections import OrderedDict as od


class choice_function():
    def __init__(self, n, choiceName):
        choiceValueDict=np.load(choiceName, allow_pickle=True).item()
        self.choiceValueDict=choiceValueDict
        self.n=n
        
    def main(self):
        choiceValueDict=self.choiceValueDict
        n=self.n
        numeric=n
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
        return df
    
if __name__=="__main__":
    n=0
    df=choice_function(n).main()
    print(df)