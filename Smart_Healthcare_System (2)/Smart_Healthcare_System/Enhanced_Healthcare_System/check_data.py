import pandas as pd

data = pd.read_csv('Health.csv')

print('Unique values per column:')
print('='*60)
for col in ['bodypain','Hollow','cough','fever','chest pain','stomach pain','diarrhea','omitting']:
    unique_vals = sorted(data[col].unique())
    print(f'{col:20s}: {unique_vals}')

print('\n\nValue ranges:')
print('='*60)
print(f"Fever range: {data['fever'].min()} to {data['fever'].max()}")
print(f"Most common fever values: {data['fever'].value_counts().head()}")
