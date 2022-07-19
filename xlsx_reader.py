import pandas as pd

data = pd.read_excel('retention drew binsky.xlsx', skiprows=2)
dd = pd.DataFrame(data)

print(dd)
A = dd['Group A'].dropna().values.tolist()
print(A)
B = dd['Group B'].dropna().values.tolist()
print(B)
C = dd['Group C'].dropna().values.tolist()
D = dd['Group D'].dropna().values.tolist()
print(D)
E = dd['Group E'].dropna().values.tolist()
print(E)
F = dd['Group F'].dropna().values.tolist()
print(F)

