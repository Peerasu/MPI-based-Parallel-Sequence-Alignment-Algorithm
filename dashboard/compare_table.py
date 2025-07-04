import pandas as pd
import sys

file_path = sys.argv[1]
formatted_tsv_path = sys.argv[2]

df = pd.read_csv(file_path, sep='\t', header=0)

max_width_step = max(df["Step Name"].astype(str).apply(len).max(), len("Step Name")) + 2
max_width_total_seq = max(df["Total Sequences"].astype(str).apply(len).max(), len("Total Sequences")) + 2
max_width_percentage = max(df["% Compare to Previous Step"].astype(str).apply(len).max(), len("% Compare to Previous Step")) + 2
max_width_seq_length = max(df["Sequence Length"].astype(str).apply(len).max(), len("Sequence Length")) + 2
max_width_flagged_quality = max(df["Sequences Flagged as Poor Quality"].astype(str).apply(len).max(), len("Sequences Flagged as Poor Quality")) + 2
max_width_gc = max(df["%GC"].astype(str).apply(len).max(), len("%GC")) + 2

formatted_output = []

border = (
    f"+{'-' * max_width_step}+{'-' * max_width_total_seq}+{'-' * max_width_percentage}+"
    f"{'-' * max_width_seq_length}+{'-' * max_width_flagged_quality}+{'-' * max_width_gc}+"
)
header = (
    f"| {'Step Name':<{max_width_step - 2}} | {'Total Sequences':<{max_width_total_seq - 2}} | "
    f"{'% Compare to Previous Step':<{max_width_percentage - 2}} | {'Sequence Length':<{max_width_seq_length - 2}} | "
    f"{'Sequences Flagged as Poor Quality':<{max_width_flagged_quality - 2}} | {'%GC':<{max_width_gc - 2}} |"
)
formatted_output.append(border)
formatted_output.append(header)
formatted_output.append(border.replace('-', '='))

for index, row in df.iterrows():
    formatted_output.append(
        f"| {row['Step Name']:<{max_width_step - 2}} | {row['Total Sequences']:<{max_width_total_seq - 2}} | "
        f"{row['% Compare to Previous Step']:<{max_width_percentage - 2}} | {row['Sequence Length']:<{max_width_seq_length - 2}} | "
        f"{row['Sequences Flagged as Poor Quality']:<{max_width_flagged_quality - 2}} | {row['%GC']:<{max_width_gc - 2}} |"
    )
    formatted_output.append(border)

with open(formatted_tsv_path, 'w') as formatted_file:
    formatted_file.write("\n".join(formatted_output))

print(f"Formatted output saved to {formatted_tsv_path}")
