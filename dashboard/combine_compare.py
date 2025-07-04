import sys
import os
import pandas as pd

def main():
    if len(sys.argv) != 4:
        print("Usage: python combine_compare.py <compare1_tsv> <compare2_tsv> <out_summary_tsv>")
        sys.exit(1)

    compare1_path = sys.argv[1]
    compare2_path = sys.argv[2]
    out_summary = sys.argv[3]

    if not os.path.isfile(compare1_path):
        print(f"Error: Compare-1 TSV file '{compare1_path}' does not exist.")
        sys.exit(1)
    if not os.path.isfile(compare2_path):
        print(f"Error: Compare-2 TSV file '{compare2_path}' does not exist.")
        sys.exit(1)

    try:
        df1 = pd.read_csv(compare1_path, sep='\t')
        df2 = pd.read_csv(compare2_path, sep='\t')

        if not df1.columns.equals(df2.columns):
            print("Error: The two TSV files have different headers.")
            sys.exit(1)

        summary_lines = []
        
        summary_lines.append("Strand 1\n")
        summary_lines.append(df1.to_csv(sep='\t', index=False))
        summary_lines.append("\n")

        summary_lines.append("Strand 2\n")
        summary_lines.append(df2.to_csv(sep='\t', index=False))
        summary_lines.append("\n")

        out_dir = os.path.dirname(out_summary)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        with open(out_summary, "w", encoding="utf-8") as outfile:
            outfile.writelines(summary_lines)

        print(f"Summary TSV has been successfully created at '{out_summary}'.")

    except Exception as e:
        print(f"An error occurred while combining TSV files: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
