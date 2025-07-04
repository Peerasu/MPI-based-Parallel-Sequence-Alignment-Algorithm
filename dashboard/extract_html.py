import sys
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import os
import pandas as pd

file_path = sys.argv[1]
tsv_path = sys.argv[2]
output_dir = sys.argv[3]

with open(file_path, 'r') as file:
    soup = BeautifulSoup(file, 'html.parser')

data = {}

summary_items = soup.select('div.summary ul li')
summary_data = []
for item in summary_items:
    status_img = item.find('img')
    status = status_img['alt'] if status_img else 'N/A'
    section_name = item.find('a').text if item.find('a') else 'N/A'
    summary_data.append([section_name, status])
data["Summary"] = summary_data

modules = soup.select('div.module')
for module in modules:
    header = module.find('h2').text.strip() if module.find('h2') else 'N/A'
    if header == "Basic Statistics":
        table = module.find('table')
        if table:
            rows = table.find_all('tr')
            module_data = []
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.text.strip() for cell in cells]
                if len(row_data) == 2:
                    module_data.append(row_data)
            data[header] = module_data

output_lines = []
for section, entries in data.items():
    output_lines.append(f"{section}")
    for entry in entries:
        output_lines.append("\t" + "\t".join(entry))
    output_lines.append("")

with open(tsv_path, 'w') as tsv_file:
    tsv_file.write("\n".join(output_lines))

print(f"Data extracted and saved to {tsv_path}")

os.makedirs(output_dir, exist_ok=True)

for module in modules:
    header = module.find('h2').text.strip() if module.find('h2') else 'N/A'
    if header == "Overrepresented sequences":
        table = module.find('table')
        if table:
            rows = table.find_all('tr')
            overrep_data = []
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.text.strip() for cell in cells]
                overrep_data.append(row_data)

            font = ImageFont.load_default()
            padding = 20
            max_col_widths = [max(len(str(cell)) for cell in col) * 10 for col in zip(*overrep_data)]
            image_width = sum(max_col_widths) + padding * (len(max_col_widths) + 1)
            image_height = (len(overrep_data) + 1) * 30

            img = Image.new("RGB", (image_width, image_height), "white")
            draw = ImageDraw.Draw(img)

            y = padding
            for row in overrep_data:
                x = padding
                for i, cell in enumerate(row):
                    draw.text((x, y), cell, fill="black", font=font)
                    x += max_col_widths[i] + padding
                y += 30

            output_file_path = os.path.join(output_dir, "Overrepresented_sequences.png")
            img.save(output_file_path)
            print(f"Saved: {output_file_path}")

images = soup.find_all('img', {'src': lambda x: x and x.startswith('data:image/png;base64,')})
for idx, img_tag in enumerate(images):
    parent_header = img_tag.find_previous('h2')
    if parent_header and parent_header.text.strip() in [
        "Per base sequence quality", "Per tile sequence quality", "Per sequence quality scores",
        "Per base sequence content", "Per sequence GC content", "Per base N content",
        "Sequence Length Distribution", "Sequence Duplication Levels", "Adapter Content"
    ]:
        base64_str = img_tag['src'].replace('data:image/png;base64,', '')
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        output_file_path = os.path.join(output_dir, f"{parent_header.text.strip().replace(' ', '_')}.png")
        image.save(output_file_path)
        print(f"Saved: {output_file_path}")

print(f"Images extracted and saved in '{output_dir}' directory")
