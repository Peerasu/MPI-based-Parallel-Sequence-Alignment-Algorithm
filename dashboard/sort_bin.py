import os
import sys
import csv

if len(sys.argv) != 3:
    print("Usage: python sort_bin.py <input_tsv> <output_tsv>")
    sys.exit(1)

input_tsv = sys.argv[1]
output_tsv = sys.argv[2]

def extract_numeric_bin_id(bin_id):
    prefix, num = bin_id.rsplit('.', 1)
    return prefix, int(num)

try:
    with open(input_tsv, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        header = next(reader)
        rows = list(reader)

        sorted_rows = sorted(rows, key=lambda row: extract_numeric_bin_id(row[0]))

    with open(output_tsv, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(header)
        writer.writerows(sorted_rows)

    print(f"Sorted TSV file '{output_tsv}' has been created successfully.")

except Exception as e:
    print(f"Error: {e}")
