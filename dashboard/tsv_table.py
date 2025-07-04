import pandas as pd
import sys

file_path = sys.argv[1]
formatted_tsv_path = sys.argv[2]

df = pd.read_csv(file_path, sep='\t', header=None, names=["Section", "Detail", "Value"], skip_blank_lines=False)

max_width_section = max(df["Section"].astype(str).apply(len).max(), len("Section")) + 2
max_width_detail = max(df["Detail"].astype(str).apply(len).max(), len("Detail")) + 2
max_width_value = max(df["Value"].astype(str).apply(len).max(), len("Value")) + 2

formatted_output = []

border = f"+{'-' * max_width_section}+{'-' * max_width_detail}+{'-' * max_width_value}+"
header = f"| {'Section':<{max_width_section - 2}} | {'Detail':<{max_width_detail - 2}} | {'Value':<{max_width_value - 2}} |"
formatted_output.append(border)
formatted_output.append(header)
formatted_output.append(border.replace('-', '='))

current_section = None

for index, row in df.iterrows():
    section = row["Section"]
    detail = row["Detail"]
    value = row["Value"]

    if pd.isna(section) and pd.isna(detail) and pd.isna(value):
        formatted_output.append(f"| {'':<{max_width_section - 2}} | {'':<{max_width_detail - 2}} | {'':<{max_width_value - 2}} |")
        continue

    if not pd.isna(section):
        current_section = section
        formatted_output.append(border)
        formatted_output.append(f"| {current_section:<{max_width_section - 2}} | {'':<{max_width_detail - 2}} | {'':<{max_width_value - 2}} |")
        formatted_output.append(border)

    if not pd.isna(detail):
        formatted_output.append(f"| {'':<{max_width_section - 2}} | {detail:<{max_width_detail - 2}} | {value:<{max_width_value - 2}} |")
        formatted_output.append(border)

with open(formatted_tsv_path, 'w') as formatted_file:
    formatted_file.write("\n".join(formatted_output))

print(f"Formatted output saved to {formatted_tsv_path}")
