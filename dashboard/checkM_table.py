import pandas as pd
import sys

file_path = sys.argv[1]
formatted_tsv_path = sys.argv[2]

df = pd.read_csv(file_path, sep='\t', header=0)

def format_value(value, width):
    if isinstance(value, float):
        return f" {value:>{width - 2}.2f} "
    elif isinstance(value, int):
        return f" {value:>{width - 2}} "
    else:
        return f" {str(value):<{width - 2}} "

column_widths = [max(df[col].astype(str).apply(len).max(), len(col)) + 2 for col in df.columns]

formatted_output = []

border = '+' + '+'.join(['-' * width for width in column_widths]) + '+'
header = '|' + '|'.join([f' {col:<{width - 2}} ' for col, width in zip(df.columns, column_widths)]) + '|'
formatted_output.append(border)
formatted_output.append(header)
formatted_output.append(border.replace('-', '='))

for index, row in df.iterrows():
    row_values = [format_value(value, width) for value, width in zip(row, column_widths)]
    formatted_output.append('|' + '|'.join(row_values) + '|')
    formatted_output.append(border)

with open(formatted_tsv_path, 'w') as formatted_file:
    formatted_file.write("\n".join(formatted_output))

print(f"Formatted output saved to {formatted_tsv_path}")

