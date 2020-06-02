import pandas as pd

df = pd.read_csv('data.csv')
input = 3
print((df['num']-input).abs().argsort())