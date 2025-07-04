#!/usr/bin/env python3

import os
import sys

def edit_tsv(input_path, output_path):
    basic_informations_keys = ["Filename", "File type", "Encoding"]

    sections = {}
    current_section = None
    sections_order = []

    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                stripped_line = line.rstrip('\n')

                if not stripped_line.startswith('\t') and stripped_line.strip() != '':
                    current_section = stripped_line.strip()
                    sections_order.append(current_section)
                    sections[current_section] = []
                elif stripped_line.strip() == '':
                    continue
                else:
                    if current_section is not None:
                        sections[current_section].append(stripped_line.lstrip('\t'))
                    else:
                        print("Warning: Data line found before any section header.")

        if "Summary" in sections:
            summary_data = sections["Summary"]
            if not summary_data or summary_data[0].strip() != "Measure\tValue":
                summary_data.insert(0, "Measure\tValue")
                sections["Summary"] = summary_data
        else:
            print("Warning: 'Summary' section not found in the TSV file.")

        if "Basic Statistics" in sections:
            basic_stats_data = sections["Basic Statistics"]

            if basic_stats_data and basic_stats_data[0].strip() == "Measure\tValue":
                basic_stats_data = basic_stats_data[1:]
                sections["Basic Statistics"] = basic_stats_data
            else:
                print("Warning: 'Basic Statistics' section does not start with 'Measure\tValue'.")

            basic_informations_data = []
            remaining_basic_stats_data = []

            for row in basic_stats_data:
                parts = row.split('\t')
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = '\t'.join(parts[1:]).strip()

                    if key in basic_informations_keys:
                        basic_informations_data.append(row)
                    else:
                        remaining_basic_stats_data.append(row)
                else:
                    remaining_basic_stats_data.append(row)

            del sections["Basic Statistics"]
            sections_order.remove("Basic Statistics")

            if basic_informations_data:
                sections_order.append("Basic Informations")
                if not basic_informations_data or basic_informations_data[0].strip() != "Measure\tValue":
                    basic_informations_data.insert(0, "Measure\tValue")
                sections["Basic Informations"] = basic_informations_data

            if remaining_basic_stats_data:
                sections_order.append("Basic Statistics")
                remaining_basic_stats_data.insert(0, "Measure\tValue")
                sections["Basic Statistics"] = remaining_basic_stats_data
        else:
            print("Warning: 'Basic Statistics' section not found in the TSV file.")

        with open(output_path, 'w', encoding='utf-8') as outfile:
            for idx, section in enumerate(sections_order):
                outfile.write(f"{section}\n")
                for row in sections[section]:
                    outfile.write(f"\t{row}\n")
                
                if idx != len(sections_order) - 1:
                    outfile.write("\n")

        print(f"Edited TSV file has been saved to '{output_path}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_path}' does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while processing the TSV file: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python edit_tsv.py <input_tsv_path> <output_tsv_path>")
        sys.exit(1)

    input_tsv = sys.argv[1]
    output_tsv = sys.argv[2]

    edit_tsv(input_tsv, output_tsv)

if __name__ == "__main__":
    main()
