import os
import sys
import re
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Transform Assembly TSV file structure.')
    parser.add_argument('input_tsv', type=str, help='Path to the input Assembly TSV file.')
    parser.add_argument('output_tsv', type=str, help='Path to save the edited TSV file.')
    return parser.parse_args()

def is_number(s):
    temp = s.strip()
    if temp.endswith('%'):
        temp = temp[:-1].strip()
    
    if '-' in temp:
        parts = temp.split('-')
        return all(part.isdigit() for part in parts)
    else:
        try:
            float(temp)
            return True
        except ValueError:
            return False

def format_number(num_str):
    original = num_str.strip()
    is_percent = False
    
    if original.endswith('%'):
        is_percent = True
        original = original[:-1].strip()
    
    try:
        if '-' in original:
            parts = original.split('-')
            formatted_parts = []
            for part in parts:
                if part.isdigit():
                    formatted_parts.append(f"{int(part):,}")
                else:
                    float_val = float(part)
                    if float_val.is_integer():
                        float_val = int(float_val)
                    formatted_parts.append(f"{float_val:,}")
            formatted_str = '-'.join(formatted_parts)
        else:
            float_val = float(original)
            if float_val.is_integer():
                float_val = int(float_val)
            formatted_str = f"{float_val:,}"
    except:
        formatted_str = original
    
    if is_percent:
        formatted_str += '%'
    
    return formatted_str

def generate_image_html(step_path):
    return ""

def generate_table_html(step_path, step):
    tsv_file = None
    for file_name in os.listdir(step_path):
        if file_name.endswith(".tsv"):
            tsv_file = os.path.join(step_path, file_name)
            break
    
    if not tsv_file:
        return "<p>No table available for this step.</p>"
    
    with open(tsv_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    contigs_section = []
    total_length_section = []
    other_info_section = []
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        
        contigs_match = re.match(r"# contigs \(>= (\d+) bp\)\s+(\d+)", line)
        if contigs_match:
            size = contigs_match.group(1)
            count = contigs_match.group(2)
            contigs_section.append((f">= {size}", count))
            continue
        
        total_length_match = re.match(r"Total length \(>= (\d+) bp\)\s+(\d+)", line)
        if total_length_match:
            size = total_length_match.group(1)
            length = total_length_match.group(2)
            total_length_section.append((f">= {size}", length))
            continue
        
        other_info_match = re.match(r"([^	]+)\s+(.+)", line)
        if other_info_match:
            measure = other_info_match.group(1).strip()
            value = other_info_match.group(2).strip()
            other_info_section.append((measure, value))
            continue
    
    new_tsv_content = ""
    
    new_tsv_content += "Number of contigs\n"
    new_tsv_content += "# contigs (bp)\tscaffolds\n"
    for size, count in contigs_section:
        new_tsv_content += f"{size}\t{count}\n"
    
    new_tsv_content += "\n"
    
    new_tsv_content += "Total length\n"
    new_tsv_content += "Length (bp)\tscaffolds\n"
    for size, length in total_length_section:
        new_tsv_content += f"{size}\t{length}\n"
    
    new_tsv_content += "\n"
    
    new_tsv_content += "Other Informations\n"
    new_tsv_content += "Measure\tValue\n"
    for measure, value in other_info_section:
        new_tsv_content += f"{measure}\t{value}\n"
    
    return new_tsv_content

def main():
    input_tsv = sys.argv[1]
    output_tsv = sys.argv[2]
    
    if not os.path.isfile(input_tsv):
        print(f"Error: Input TSV file '{input_tsv}' does not exist.")
        sys.exit(1)
    
    step_name = os.path.basename(os.path.dirname(input_tsv))
    
    edited_tsv = generate_table_html(os.path.dirname(input_tsv), step_name)
    
    with open(output_tsv, "w", encoding="utf-8") as outfile:
        outfile.write(edited_tsv)
    
    print(f"Edited TSV file has been saved to '{output_tsv}'.")

if __name__ == "__main__":
    main()
