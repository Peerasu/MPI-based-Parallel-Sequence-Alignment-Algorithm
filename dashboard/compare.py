import os
import pandas as pd
import sys

dashboard_dir = sys.argv[1]
output_tsv = sys.argv[2]
strand=sys.argv[3]

steps = [f"Rawdata-{strand}", f"Trimming-{strand}", f"Alignment-{strand}"]

summary_data = []

prev_total_sequences = None

for step in steps:
    step_path = os.path.join(dashboard_dir, step)
    tsv_files = [f for f in os.listdir(step_path) if f.endswith(".tsv")]
    
    for tsv_file in tsv_files:
        tsv_path = os.path.join(step_path, tsv_file)
        
        with open(tsv_path, 'r') as file:
            lines = file.readlines()
        
        in_basic_statistics = False
        total_sequences = None
        sequence_length = None
        flagged_quality = None
        gc_content = None
        
        for line in lines:
            line = line.strip()
            
            if line == "Basic Statistics":
                in_basic_statistics = True
                continue
            
            if not line and in_basic_statistics:
                break
            
            if in_basic_statistics:
                parts = line.split('\t')
                if len(parts) == 2:
                    measure, value = parts
                    if measure == "Total Sequences":
                        total_sequences = int(value)
                    elif measure == "Sequence length":
                        sequence_length = value
                    elif measure == "Sequences flagged as poor quality":
                        flagged_quality = int(value)
                    elif measure == "%GC":
                        gc_content = value
        
        if total_sequences is not None:
            if prev_total_sequences is None:
                percentage = "100%"
            else:
                percentage = f"{(total_sequences / prev_total_sequences) * 100:.2f}%"
            
            if step==f"Rawdata-{strand}":
                new_step_name=f"Raw data QC"
            elif step==f"Trimming-{strand}":
                new_step_name=f"Adapter and quality trimming QC"
            elif step==f"Alignment-{strand}":
                new_step_name=f"Reads without host DNA QC"
            else:
                new_step_name=step
            
            summary_data.append([
                new_step_name, total_sequences, percentage, sequence_length, flagged_quality, gc_content
            ])
            
            prev_total_sequences = total_sequences
        
        break

summary_df = pd.DataFrame(summary_data, columns=[
    "Step Name", "Total Sequences", "Percentage of Sequences Compared to the Previous Step", "Sequence Length", 
    "Sequences Flagged as Poor Quality", "%GC"
])

summary_df.to_csv(output_tsv, sep='\t', index=False)

print(f"Summary of QC for strand {strand} saved to {output_tsv}")
