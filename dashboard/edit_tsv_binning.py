import sys
import pandas as pd
import os

def main():
    if len(sys.argv) != 3:
        print("Usage: python edit_binning_tsv.py <input_tsv> <output_tsv>")
        sys.exit(1)

    input_tsv = sys.argv[1]
    output_tsv = sys.argv[2]

    if not os.path.isfile(input_tsv):
        print(f"Error: Input TSV file '{input_tsv}' does not exist.")
        sys.exit(1)

    try:
        df = pd.read_csv(input_tsv, sep='\t')

        required_columns = ["Bin Id", "Completeness"]
        for col in required_columns:
            if col not in df.columns:
                print(f"Error: Required column '{col}' not found in the TSV file.")
                sys.exit(1)

        df["Bin Id"] = df["Bin Id"].str.replace("Mag.bins.", "", regex=False)

        df["Completeness"] = pd.to_numeric(df["Completeness"], errors='coerce')

        df = df.dropna(subset=["Completeness"])

        df_sorted = df.sort_values(by="Completeness", ascending=False).reset_index(drop=True)

        df_sorted.to_csv(output_tsv, sep='\t', index=False)

        print(f"Edited TSV has been saved to '{output_tsv}'.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
