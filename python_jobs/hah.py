import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})

# Perform rolling window calculation (e.g., rolling sum with window size 2)
rolling_sum = df['value'].rolling(window=2).sum()

# Perform expanding window calculation (e.g., expanding sum)
expanding_sum = df['value'].expanding().sum()

print("Original DataFrame:")
print(df)
print("\nRolling Sum:")
print(rolling_sum)
print("\nExpanding Sum:")
print(expanding_sum)

