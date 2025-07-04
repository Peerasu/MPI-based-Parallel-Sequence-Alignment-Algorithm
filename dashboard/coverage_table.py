import pandas as pd
import sys

file_path = sys.argv[1]
formatted_tsv_path = sys.argv[2]

df = pd.read_csv(file_path, sep='\t', header=None, names=["Detail", "Value"], skip_blank_lines=False)

max_width_detail = max(df["Detail"].astype(str).apply(len).max(), len("Detail")) + 2
max_width_value = max(df["Value"].astype(str).apply(len).max(), len("Value")) + 2

formatted_output = []

border = f"+{'-' * max_width_detail}+{'-' * max_width_value}+"
header = f"| {'Detail':<{max_width_detail - 2}} | {'Value':>{max_width_value - 2}} |"
formatted_output.append(border)
formatted_output.append(header)
formatted_output.append(border.replace('-', '='))

for index, row in df.iterrows():
    detail = row["Detail"]
    value = row["Value"]

    if pd.isna(detail) and pd.isna(value):
        formatted_output.append(f"| {'':<{max_width_detail - 2}} | {'':>{max_width_value - 2}} |")
        continue

    if pd.api.types.is_numeric_dtype(type(value)):
        try:
            value = float(value)
            value = f"{value:.2f}"
        except ValueError:
            pass

    formatted_output.append(f"| {detail:<{max_width_detail - 2}} | {value:>{max_width_value - 2}} |")
    formatted_output.append(border)

with open(formatted_tsv_path, 'w') as formatted_file:
    formatted_file.write("\n".join(formatted_output))

print(f"Formatted output saved to {formatted_tsv_path}")

