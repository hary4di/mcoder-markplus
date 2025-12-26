import pandas as pd

# Read file
df = pd.read_excel(r'C:\Users\hp\OneDrive - MarkPlus Indonesia ,PT\MARKPLUS\Automation\koding\files\uploads\Raw_Data_ASDP_Berkendara.xlsx')

print('=== ANALYSIS: Multi-Label Classification Results ===\n')

# Count multi-label (contains space)
multi = df[df['E1_coded'].astype(str).str.contains(' ', na=False)]
single = df[(df['E1_coded'].notna()) & (~df['E1_coded'].astype(str).str.contains(' ', na=False)) & (df['E1_coded'] != 99)]

print(f'Total responses with E1_coded: {df["E1_coded"].notna().sum()}')
print(f'Multi-label responses (with space): {len(multi)}')
print(f'Single-label responses: {len(single)}')
print(f'Invalid (code 99): {(df["E1_coded"] == 99).sum()}')

print('\n=== Sample Multi-Label Cases ===')
if len(multi) > 0:
    print(multi[['E1', 'E1_coded']].head(15).to_string(index=False))
else:
    print('NO MULTI-LABEL FOUND!')

print('\n=== Responses with "dan" or "," (should be multi?) ===')
test = df[df['E1'].astype(str).str.contains('dan|,', case=False, na=False) & 
          (df['E1_coded'].notna()) & 
          (~df['E1_coded'].astype(str).str.contains(' ', na=False))]
print(f'Found {len(test)} responses with "dan"/"," but single code')
print(test[['E1', 'E1_coded']].head(20).to_string(index=False))

print('\n=== Check E1_coded data types ===')
print(f'E1_coded dtype: {df["E1_coded"].dtype}')
print(f'Sample E1_coded values (first 30 non-null):')
print(df[df['E1_coded'].notna()]['E1_coded'].head(30).tolist())
