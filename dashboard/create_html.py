import os
import sys
import base64
import urllib.parse

###################################################################
if len(sys.argv) != 4:
    print("Usage: python create_html.py <dashboard_directory> <output_html> <name>")
    sys.exit(1)

dashboard_dir = sys.argv[1]
output_html   = sys.argv[2]
name          = sys.argv[3]

###################################################################
# Step configuration

steps = [
    "Rawdata-1", "Rawdata-2",
    "Trimming-1", "Trimming-2",
    "Alignment-1", "Alignment-2",
    "Assembly", "Binning",
    "Summary"
]

visualize_steps = [
    "Rawdata-1", "Rawdata-2",
    "Trimming-1", "Trimming-2",
    "Alignment-1", "Alignment-2"
]

multi_sort_table_steps = [
    "Rawdata-1", "Rawdata-2",
    "Trimming-1", "Trimming-2",
    "Alignment-1", "Alignment-2",
    "Assembly"
]


official_titles = {
    "Rawdata-1": "Raw data QC for strand 1",
    "Rawdata-2": "Raw data QC for strand 2",
    "Trimming-1": "Adapter and quality trimming QC for strand 1",
    "Trimming-2": "Adapter and quality trimming QC for strand 2",
    "Alignment-1": "Reads without host DNA QC for strand 1",
    "Alignment-2": "Reads without host DNA QC for strand 2",
    "Assembly": "Metagenomic assembly result",
    "Binning": "MAGs quality assessment result",
    "Summary": "Summary"
}

###################################################################
# Image embedding

def generate_image_html(step_path):
    image_dir = os.path.join(step_path, "Visualize_QC")
    if not os.path.exists(image_dir):
        return ""
    image_html = ""
    image_show = [
        "Per_base_sequence_quality.png",
        "Per_base_sequence_content.png",
        "Per_sequence_GC_content.png",
        "Per_sequence_quality_scores.png",
        "Sequence_Duplication_Levels.png",
        "Sequence_Length_Distribution.png"
    ]
    for image_file in image_show:
        if image_file.endswith(".png"):
            image_path = os.path.join(image_dir, image_file)
            try:
                with open(image_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                image_name = os.path.splitext(image_file)[0].replace('_', ' ').title()
                image_html += f"""
                <div class='image-wrapper'>
                    <h3 class='image-title'>{image_name}</h3>
                    <img src="data:image/png;base64,{encoded}" alt="{image_file}">
                </div>
                """
            except Exception as e:
                print(f"[Warning] Error encoding image {image_path}: {e}")
    return image_html

###################################################################
def is_number(s):
    temp = s.strip()
    if temp.endswith('%'):
        temp = temp[:-1].strip()
    if '-' in temp:
        parts = temp.split('-')
        return all(part.replace('.', '', 1).isdigit() for part in parts)
    else:
        try:
            float(temp)
            return True
        except ValueError:
            return False

def format_number(num_str, col_type):
    original = num_str.strip()
    is_percent = False

    if original.endswith('%'):
        is_percent = True
        original = original[:-1].strip()

    if '-' in original:
        parts = original.split('-')
        formatted_parts = []
        for part in parts:
            if part.isdigit():
                if col_type == 'float':
                    formatted_parts.append(f"{float(part):,.2f}")
                else:
                    formatted_parts.append(f"{int(part):,}")
            else:
                try:
                    val = float(part)
                    if col_type == 'float':
                        formatted_parts.append(f"{val:,.2f}")
                    else:
                        formatted_parts.append(f"{int(val):,}")
                except ValueError:
                    formatted_parts.append(part)
        formatted = '-'.join(formatted_parts)
    else:
        try:
            val = float(original)
            if col_type == 'float':
                formatted = f"{val:,.2f}"
            else:
                formatted = f"{int(val):,}"
        except ValueError:
            formatted = original

    if is_percent:
        formatted += '%'
    return formatted

def determine_column_types(headers, rows):
    col_types = ['int'] * len(headers)
    for i in range(len(headers)):
        for row in rows:
            if i >= len(row):
                continue
            cell = row[i].strip()
            if cell in ["[PASS]", "[WARNING]", "[FAIL]", "[FAILED]"] or cell == '':
                continue
            local_cell = cell
            if '-' in local_cell:
                parts = local_cell.split('-')
                for part in parts:
                    if not part.replace('.', '', 1).isdigit():
                        col_types[i] = 'str'
                        break
                    if '.' in part:
                        col_types[i] = 'float'
                        break
                if col_types[i] == 'str':
                    break
                continue
            if local_cell.endswith('%'):
                local_cell = local_cell[:-1].strip()
            try:
                if '.' in local_cell:
                    float(local_cell)
                    col_types[i] = 'float'
                else:
                    int(local_cell)
            except ValueError:
                col_types[i] = 'str'
                break
    return col_types

###################################################################
def generate_table_html(step_path, step):
    if step == "Summary":
        summary_filename = f"{name}_Summary.tsv"
        summary_tsv_path = os.path.join(step_path, summary_filename)
        if not os.path.isfile(summary_tsv_path):
            return f"<p>{summary_filename} file does not exist.</p>"
        try:
            with open(summary_tsv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {summary_filename}: {e}")
            return f"<p>Error loading {summary_filename} file.</p>"
        current_strand = None
        tables = {"Strand 1": {"headers": [], "rows": []},
                  "Strand 2": {"headers": [], "rows": []}}
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("Strand"):
                current_strand = stripped
                continue
            if current_strand and not tables[current_strand]['headers']:
                headers = stripped.split("\t")
                tables[current_strand]['headers'] = headers
                continue
            if current_strand and tables[current_strand]['headers']:
                row = stripped.split("\t")
                if row == tables[current_strand]['headers']:
                    continue
                tables[current_strand]['rows'].append(row)
        combined_content = "\n".join(lines)
        encoded_summary_tsv = base64.b64encode(combined_content.encode('utf-8')).decode('utf-8')
        download_button = f'''
            <a href="data:text/tab-separated-values;base64,{encoded_summary_tsv}"
               download="{summary_filename}"
               class="download-button">Download TSV</a>
        </div>
        <hr class="blue-line">
        '''
        html_content = download_button
        table_html = ""
        for strand, content in tables.items():
            headers = content['headers']
            rows = content['rows']
            if not headers or not rows:
                continue
            col_types = determine_column_types(headers, rows)
            table_html += f"""
            <div class='summary-table'>
                <h2 class='section-title'>A summary of data processing for {strand.lower()}</h2>
                <table class='tablesort'>
                    <thead><tr>
            """
            for header in headers:
                table_html += f"<th>{header}</th>"
            table_html += "</tr></thead>\n<tbody>\n"
            for row in rows:
                table_html += "<tr>"
                for i, col in enumerate(row):
                    status_class = ""
                    if col.strip() in ["[PASS]", "[WARNING]", "[FAIL]", "[FAILED]"]:
                        if col.strip() == "[PASS]":
                            status_class = "status-pass"
                        elif col.strip() == "[WARNING]":
                            status_class = "status-warning"
                        else:
                            status_class = "status-fail"
                    if is_number(col):
                        formatted_num = format_number(col, col_types[i])
                        table_html += f"<td style='text-align: right;'>{formatted_num}</td>"
                    elif status_class:
                        table_html += f"<td class='{status_class}'>{col}</td>"
                    else:
                        table_html += f"<td>{col}</td>"
                table_html += "</tr>\n"
            table_html += "</tbody>\n</table>\n</div>\n"
        html_content += table_html
        return html_content

    ################################################################
    tsv_file = None
    for file_name in os.listdir(step_path):
        if file_name.endswith(".tsv"):
            tsv_file = os.path.join(step_path, file_name)
            break
    if not tsv_file:
        return "<p>No table available for this step.</p>"
    table_html = ""
    with open(tsv_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if step in multi_sort_table_steps:
        table_sections = []
        current_section = None
        for line in lines:
            stripped = line.strip()
            if not stripped:
                current_section = None
                continue
            if '\t' not in stripped:
                current_section = {
                    'title': stripped,
                    'headers': [],
                    'rows': []
                }
                table_sections.append(current_section)
            elif current_section and not current_section['headers']:
                headers = stripped.split('\t')
                current_section['headers'] = headers
            elif current_section and current_section['headers']:
                parts = stripped.split('\t')
                if len(parts) >= len(current_section['headers']):
                    current_section['rows'].append(parts)
                else:
                    current_section['rows'].append(parts + ['']*(len(current_section['headers']) - len(parts)))
        if not table_sections:
            return "<p>No table available for this step.</p>"
        table_html += "<div class='tables-container'>\n"
        for section in table_sections:
            table_name = section['title']
            headers = section['headers']
            rows = section['rows']
            col_types = determine_column_types(headers, rows)
            if step == "Assembly" and table_name.strip().lower() == "other informations":
                try:
                    value_col_index = headers.index("Value")
                except ValueError:
                    value_col_index = None
            else:
                value_col_index = None
            table_html += f"""
            <div class='single-table'>
                <h2 class='section-title'>{table_name}</h2>
                <table class='tablesort'>
                    <thead><tr>
            """
            for header in headers:
                table_html += f"<th>{header}</th>"
            table_html += "</tr></thead>\n<tbody>\n"
            for row in rows:
                table_html += "<tr>"
                for i, col in enumerate(row):
                    status_class = ""
                    if col.strip() == "[PASS]":
                        status_class = "status-pass"
                    elif col.strip() == "[WARNING]":
                        status_class = "status-warning"
                    elif col.strip() in ["[FAIL]", "[FAILED]"]:
                        status_class = "status-fail"
                    if is_number(col):
                        if step == "Assembly" and table_name.strip().lower() == "other informations" and i == value_col_index:
                            try:
                                num = float(col)
                                if num.is_integer():
                                    formatted_num = f"{int(num):,}"
                                else:
                                    formatted_num = f"{num:,.2f}"
                            except ValueError:
                                formatted_num = col
                            table_html += f"<td style='text-align: right;'>{formatted_num}</td>"
                        else:
                            formatted_num = format_number(col, col_types[i])
                            table_html += f"<td style='text-align: right;'>{formatted_num}</td>"
                    elif status_class:
                        table_html += f"<td class='{status_class}'>{col}</td>"
                    else:
                        table_html += f"<td>{col}</td>"
                table_html += "</tr>\n"
            table_html += "</tbody>\n</table>\n</div>\n"
        table_html += "</div>\n"

    elif step == "Binning":
        headers = []
        if len(lines) > 0:
            headers = lines[0].strip().split("\t")
        data_rows = [line.strip().split("\t") for line in lines[1:] if line.strip()]
        col_types = determine_column_types(headers, data_rows)
        table_html += "<table class='tablesort'>\n"
        if len(lines) > 0:
            table_html += "<thead><tr>\n"
            for idx, col in enumerate(headers):
                if is_number(col):
                    table_html += f"<th data-sort-method='number'>{col}</th>"
                else:
                    table_html += f"<th>{col}</th>"
            table_html += "</tr></thead>\n<tbody>\n"
            for row in data_rows:
                table_html += "<tr>"
                for i, cell in enumerate(row):
                    status_class = ""
                    if cell.strip() == "[PASS]":
                        status_class = "status-pass"
                    elif cell.strip() == "[WARNING]":
                        status_class = "status-warning"
                    elif cell.strip() in ["[FAIL]", "[FAILED]"]:
                        status_class = "status-fail"
                    if is_number(cell):
                        formatted = format_number(cell, col_types[i])
                        table_html += f"<td style='text-align: right;'"
                        if status_class:
                            table_html += f" class='{status_class}'"
                        table_html += f">{formatted}</td>"
                    elif status_class:
                        table_html += f"<td class='{status_class}'>{cell}</td>"
                    else:
                        table_html += f"<td>{cell}</td>"
                table_html += "</tr>\n"
            table_html += "</tbody>\n</table>\n"

    else:
        headers = []
        if len(lines) > 0:
            headers = lines[0].strip().split("\t")
        data_rows = [line.strip().split("\t") for line in lines[1:] if line.strip()]
        col_types = determine_column_types(headers, data_rows)
        table_html += "<table class='tablesort'>\n"
        if headers:
            table_html += "<thead><tr>"
            for i, col in enumerate(headers):
                if is_number(col):
                    table_html += f"<th data-sort-method='number'>{col}</th>"
                else:
                    table_html += f"<th>{col}</th>"
            table_html += "</tr></thead>\n<tbody>\n"
            for row in data_rows:
                table_html += "<tr>"
                for i, cell in enumerate(row):
                    status_class = ""
                    if cell.strip() == "[PASS]":
                        status_class = "status-pass"
                    elif cell.strip() == "[WARNING]":
                        status_class = "status-warning"
                    elif cell.strip() in ["[FAIL]", "[FAILED]"]:
                        status_class = "status-fail"
                    if is_number(cell):
                        formatted = format_number(cell, col_types[i])
                        table_html += f"<td style='text-align: right;'"
                        if status_class:
                            table_html += f" class='{status_class}'"
                        table_html += f">{formatted}</td>"
                    elif status_class:
                        table_html += f"<td class='{status_class}'>{cell}</td>"
                    else:
                        table_html += f"<td>{cell}</td>"
                table_html += "</tr>\n"
            table_html += "</tbody>\n</table>\n"
    return table_html

###################################################################
# Main HTML framework

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Files SRR23958655</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            display: block;
            scroll-behavior: smooth;
        }
        .sidebar {
            display: inline-block;
            white-space: nowrap;
            background-color: #f4f4f4;
            padding: 15px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            height: 100vh;
            position: fixed;
            overflow-y: auto;
            vertical-align: top;
        }
        .content {
            padding: 20px;
        }
        .sidebar a {
            display: block;
            padding: 10px;
            color: #333;
            text-decoration: none;
            margin-bottom: 5px;
            border-radius: 4px;
        }
        .sidebar a:hover {
            background-color: #ddd;
        }
        .active {
            background-color: #d3d3d3;
            color: #333;
            font-weight: bold;
        }
        table {
            border-collapse: collapse;
            margin-bottom: 20px;
            table-layout: auto;
            width: auto;
            max-width: 100%;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 8px;
            white-space: nowrap;
        }
        th {
            background-color: #f4f4f4;
            user-select: none;
            cursor: pointer;
            text-align: center;
        }
        th::before, th::after {
            content: none !important;
            display: none !important;
        }
        .status-pass {
            color: green;
            font-weight: bold;
        }
        .status-warning {
            color: orange;
            font-weight: bold;
        }
        .status-fail {
            color: red;
            font-weight: bold;
        }
        .tables-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: space-between;
        }
        .single-table {
            flex: 1;
            min-width: 300px;
        }
        .summary-container {
            display: flex;
            flex-direction: column;
            gap: 40px;
        }
        .summary-table {
            width: 100%;
        }
        @media (max-width: 1200px) {
            .tables-container {
                flex-direction: column;
            }
            .single-table {
                min-width: 100%;
            }
        }
        .step-section {
            margin-bottom: 40px;
        }
        .section-title {
            display: inline-block;
            background-color: #007bff;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 18px;
            margin-bottom: 10px;
        }
        .download-summary {
            margin-bottom: 20px;
        }
        .download-button {
            padding: 8px 12px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            margin-left: 10px;
        }
        .download-button:hover {
            background-color: #0056b3;
        }
        .image-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
            justify-content: flex-start;
        }
        .image-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            max-width: 80%;
            margin-left: 10%;
            margin-bottom: 30px;
        }
        .image-title {
            margin-bottom: 5px;
            text-align: center;
            background-color: #add8e6;
            padding: 5px 10px;
            border-radius: 5px;
            width: fit-content;
        }
        .black-line {
            border: 0;
            height: 2px;
            background-color: black;
            margin: 20px 0;
            width: 100%;
        }
        .blue-line {
            border: 0;
            height: 2px;
            background-color: #007bff;
            margin-top: 5px;
            width: 100%;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tablesort/5.2.1/tablesort.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tablesort/5.2.1/sorts/tablesort.number.min.js"></script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Adjust .content margin based on sidebar width
        const sidebar = document.querySelector('.sidebar');
        const content = document.querySelector('.content');
        const sidebarWidth = sidebar.getBoundingClientRect().width;
        content.style.marginLeft = (sidebarWidth + 20) + "px";

        // Initialize TableSort on .tablesort
        const tables = document.querySelectorAll('table.tablesort');
        tables.forEach(tbl => new Tablesort(tbl));

        // IntersectionObserver => highlight active link as user scrolls
        const sections = document.querySelectorAll('.step-section');
        const options = {
            root: null,
            rootMargin: '-50% 0px -50% 0px',
            threshold: 0
        };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.querySelector('h1').getAttribute('id');
                    // Clear existing 'active'
                    document.querySelectorAll('.sidebar a').forEach(link => link.classList.remove('active'));
                    // Activate the link for the visible section
                    const activeLink = document.querySelector(`.sidebar a[href="#${sectionId}"]`);
                    if (activeLink) {
                        activeLink.classList.add('active');
                    }
                }
            });
        }, options);

        sections.forEach(section => {
            observer.observe(section);
        });

        // Immediately highlight link on click
        const sidebarLinks = document.querySelectorAll('.sidebar a');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', () => {
                sidebarLinks.forEach(lnk => lnk.classList.remove('active'));
                link.classList.add('active');
            });
        });
    });
    </script>
</head>
<body>
    <div class="sidebar">
"""

for step in steps:
    html_content += f'        <a href="#{step}">{step}</a>\n'

html_content += """
    </div>
    <div class="content">
"""

###################################################################

for step in steps:
    step_path = os.path.join(dashboard_dir, step)
    official_title = official_titles.get(step, step)
    html_content += f'''
    <div class="step-section">
        <div style="display: flex; align-items: center; flex-wrap: wrap;">
            <h1 id="{step}" style="margin: 0; padding-bottom: 5px;">{official_title}</h1>
'''
    if not os.path.exists(step_path):
        html_content += f'''
            </div>
            <hr class="blue-line">
            <p>Directory for step "{step}" does not exist.</p>
            <hr class="black-line">
        '''
        continue

    if step == "Summary":
        summary_filename = f"{name}_Summary.tsv"
        summary_tsv_path = os.path.join(step_path, summary_filename)
        if not os.path.isfile(summary_tsv_path):
            html_content += f'''
            </div>
            <hr class="blue-line">
            <p>{summary_filename} file does not exist.</p>
            <hr class="black-line">
            '''
            continue
        try:
            with open(summary_tsv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {summary_filename}: {e}")
            html_content += f'''
            </div>
            <hr class="blue-line">
            <p>Error loading {summary_filename} file.</p>
            <hr class="black-line">
            '''
            continue
        summary_html = generate_table_html(step_path, step)
        html_content += summary_html
    else:
        tsv_file_found = None
        for f in os.listdir(step_path):
            if f.endswith(".tsv"):
                tsv_file_found = os.path.join(step_path, f)
                break
        if tsv_file_found:
            try:
                with open(tsv_file_found, "rb") as tsv_file:
                    tsv_data = tsv_file.read()
                encoded_tsv = base64.b64encode(tsv_data).decode("utf-8")
                safe_name = urllib.parse.quote(os.path.basename(tsv_file_found))
                html_content += f'''
            <a href="data:text/tab-separated-values;base64,{encoded_tsv}"
               download="{safe_name}"
               class="download-button">Download TSV</a>
        </div>
        <hr class="blue-line">
                '''
            except Exception as e:
                print(f"[Warning] Error reading TSV file {tsv_file_found}: {e}")
                html_content += '''
        </div>
        <hr class="blue-line">
        <p>Error loading TSV file.</p>
        <hr class="black-line">
                '''
                continue
        else:
            html_content += '''
        </div>
        <hr class="blue-line">
        <p>No table available for this step.</p>
        <hr class="black-line">
            '''
            continue
        step_html = generate_table_html(step_path, step)
        html_content += step_html

    if step in visualize_steps and step != "Summary":
        images_html = generate_image_html(step_path)
        html_content += images_html

    html_content += '''
        <hr class="black-line">
    </div>
    '''

html_content += """
    </div>
</body>
</html>
"""

###################################################################
# Write the final HTML output

try:
    with open(output_html, "w", encoding="utf-8") as outfile:
        outfile.write(html_content)
    print(f"Dashboard HTML file '{output_html}' has been created successfully.")
except Exception as e:
    print(f"[Error] Failed to write output HTML '{output_html}': {e}")
