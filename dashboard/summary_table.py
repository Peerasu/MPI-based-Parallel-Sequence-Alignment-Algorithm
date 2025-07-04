#!/usr/bin/env python3
import sys
import os
import math

def parse_summary_tsv(file_path):
    sections = []
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                current_section = None
                continue

            if stripped.startswith("Strand"):
                current_section = {
                    'title': stripped,
                    'headers': [],
                    'rows': []
                }
                sections.append(current_section)
            elif current_section and not current_section['headers']:
                headers = stripped.split("\t")
                current_section['headers'] = headers
                continue
            elif current_section and current_section['headers']:
                row = stripped.split("\t")
                if row == current_section['headers']:
                    continue
                if len(row) >= len(current_section['headers']):
                    current_section['rows'].append(row[:len(current_section['headers'])])
                else:
                    current_section['rows'].append(row + ['']*(len(current_section['headers']) - len(row)))

    return sections

def calculate_column_widths(headers, rows):
    num_cols = len(headers)
    max_content_widths = [len(header) for header in headers]

    for row in rows:
        for i in range(num_cols):
            if i < len(row):
                cell_length = len(row[i])
                max_content_widths[i] = max(max_content_widths[i], cell_length)
            else:
                max_content_widths[i] = max(max_content_widths[i], 0)

    adjusted_widths = [math.ceil(w * 1.2) for w in max_content_widths]

    adjusted_widths = [w + 2 for w in adjusted_widths]

    return adjusted_widths

def determine_column_types(headers, rows):
    column_types = ['int'] * len(headers)

    for i in range(len(headers)):
        for row in rows:
            if i >= len(row):
                continue
            cell = row[i].strip()
            if cell in ["[PASS]", "[WARNING]", "[FAIL]", "[FAILED]"]:
                continue 
            if cell == '':
                continue
            if '-' in cell:
                parts = cell.split('-')
                for part in parts:
                    if not part.replace('.', '', 1).isdigit():
                        column_types[i] = 'str'
                        break
                    elif '.' in part:
                        column_types[i] = 'float'
                        break
                if column_types[i] == 'str':
                    break
                continue
            if cell.endswith('%'):
                cell = cell[:-1].strip()
            try:
                if '.' in cell:
                    float(cell)
                    column_types[i] = 'float'
                else:
                    int(cell)
            except ValueError:
                column_types[i] = 'str'
                break

    return column_types

def format_number(s, col_type):
    original = s.strip()
    is_percent = False

    if original.endswith('%'):
        is_percent = True
        original = original[:-1].strip()

    if '-' in original:
        parts = original.split('-')
        formatted_parts = []
        for part in parts:
            if part.isdigit():
                formatted_parts.append(f"{int(part):,}")
            else:
                try:
                    float_val = float(part)
                    if col_type == 'float':
                        formatted_val = f"{float_val:,.2f}"
                    else:
                        formatted_val = f"{int(float_val):,}"
                    formatted_parts.append(formatted_val)
                except ValueError:
                    formatted_parts.append(part)
        formatted = '-'.join(formatted_parts)
    else:
        try:
            if col_type == 'float':
                float_val = float(original)
                formatted = f"{float_val:,.2f}"
            elif col_type == 'int':
                int_val = int(original)
                formatted = f"{int_val:,}"
            else:
                formatted = original
        except ValueError:
            formatted = original

    if is_percent:
        formatted += '%'

    return formatted

def format_section(section):
    formatted = []
    title = section['title']
    headers = section['headers']
    rows = section['rows']

    column_types = determine_column_types(headers, rows)

    widths = calculate_column_widths(headers, rows)

    border = '+' + '+'.join(['-' * width for width in widths]) + '+'
    header_line = '|' + '|'.join([f' {headers[i]:<{widths[i]-2}} ' for i in range(len(headers))]) + '|'

    formatted.append(f"Section: {title}")
    formatted.append(border)
    formatted.append(header_line)
    formatted.append(border.replace('-', '='))

    for row in rows:
        formatted_row = []
        for i in range(len(headers)):
            if i < len(row):
                cell = row[i]
                if column_types[i] in ['int', 'float']:
                    formatted_num = format_number(cell, column_types[i])
                    formatted_row.append(f' {formatted_num:>{widths[i]-2}} ')
                else:
                    formatted_row.append(f' {cell:<{widths[i]-2}} ')
            else:
                formatted_row.append(' ' * (widths[i]))
        formatted.append('|' + '|'.join(formatted_row) + '|')
        formatted.append(border)

    formatted.append('')

    return formatted

def main():
    if len(sys.argv) != 3:
        print("Usage: python summary_table.py <input_summary_tsv> <output_formatted_txt>")
        sys.exit(1)

    input_tsv = sys.argv[1]
    output_txt = sys.argv[2]

    if not os.path.isfile(input_tsv):
        print(f"Error: Input TSV file '{input_tsv}' does not exist.")
        sys.exit(1)

    sections = parse_summary_tsv(input_tsv)

    formatted_output = []

    for section in sections:
        formatted_section = format_section(section)
        formatted_output.extend(formatted_section)

    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(formatted_output))

    print(f"Formatted table saved to '{output_txt}'.")

if __name__ == "__main__":
    main()
