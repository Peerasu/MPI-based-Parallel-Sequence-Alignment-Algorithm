import sys
import csv

if len(sys.argv) != 3:
    print("Usage: python shift_column.py <input_tsv> <output_tsv>")
    sys.exit(1)

input_tsv = sys.argv[1]
output_tsv = sys.argv[2]

with open(input_tsv, 'r') as infile:
    reader = csv.reader(infile, delimiter='\t')
    header = next(reader)

    marker_lineage_index = header.index("Marker lineage")
    completeness_index = header.index("Completeness")

    new_header = header[:marker_lineage_index + 1] + [header[completeness_index]] + header[marker_lineage_index + 1:completeness_index] + header[completeness_index + 1:]

    rows = []
    for row in reader:
        new_row = row[:marker_lineage_index + 1] + [row[completeness_index]] + row[marker_lineage_index + 1:completeness_index] + row[completeness_index + 1:]
        rows.append(new_row)

with open(output_tsv, 'w', newline='') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    writer.writerow(new_header)
    writer.writerows(rows)

print(f"Column 'Completeness' has been moved next to 'Marker lineage' and saved to {output_tsv}.")