# Read the file
with open('news_volatility_analysis.py', 'r') as f:
    content = f.read()

# Fix the problematic line
old_line = "    if not np.isnan(before_vol) and not np.isnan(after_vol):"
new_line = "    if not (np.isnan(before_vol).any() if hasattr(before_vol, 'any') else np.isnan(before_vol)) and not (np.isnan(after_vol).any() if hasattr(after_vol, 'any') else np.isnan(after_vol)):"

content = content.replace(old_line, new_line)

# Write it back
with open('news_volatility_analysis.py', 'w') as f:
    f.write(content)

print("Fixed!")
