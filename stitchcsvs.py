import pandas as pd
import os
print(os.getcwd())

files = ["ECE302_FinalProject/Kdyvar/500/yErr.csv", "ECE302_FinalProject/KPyvar/600/yErr.csv", "ECE302_FinalProject/KPyvar/700/yErr.csv", "ECE302_FinalProject/KPyvar/800/yErr.csv", "ECE302_FinalProject/KPyvar/900/yErr.csv",]
column_names = ["500", "600", "700", "800", "900"]

dfs = [pd.read_csv(f, header=None) for f in files]

combined = pd.concat(dfs, axis=1)
combined.columns = column_names

combined.to_csv("KpYVarYerr.csv", index=False)