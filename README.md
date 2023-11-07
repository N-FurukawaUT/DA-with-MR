# DA-with-MR
東京大学の駒場進学選択制度を、現行のDA with majority quotaから、DA with minority reserve(Hafalirの論文を参照：https://doi.org/10.3982/TE1135)に変更した場合にどうなるかのシミュレーションです。分析用&一人用のコードであるため、過去に使っていた変数などが維持されている場合があります。ご了承ください。
シミュレーションのために実行するべきファイルはchoiceFunctrion_tuning.pyとSimulation_komaba_multiThread.pyで、前者では実データを基にした勾配降下法によるパラメータチューニングを行い、後者では実際のシミュレーションを行います。
