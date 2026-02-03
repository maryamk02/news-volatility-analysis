# Read the file
with open('news_volatility_analysis.py', 'r') as f:
    lines = f.readlines()

# Find and fix the problematic lines
for i, line in enumerate(lines):
    # Fix line 123
    if "if not np.isnan(before_vol) and not np.isnan(after_vol):" in line:
        lines[i] = "    if not pd.isna(before_vol) and not pd.isna(after_vol):\n"
    
    # Fix line 125
    if "vol_change_pct = (vol_change / before_vol) * 100 if before_vol > 0 else 0" in line:
        lines[i] = "        vol_change_pct = (vol_change / before_vol) * 100 if float(before_vol) > 0 else 0\n"

# Write it back
with open('news_volatility_analysis.py', 'w') as f:
    f.writelines(lines)

print("Fixed all pandas compatibility issues!")
