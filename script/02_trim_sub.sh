#!/bin/bash
#PBS -e parallel.err
#PBS -o parallel.log
### Mail to user
#PBS -m ae
#PBS -l walltime={{TIME}}
#PBS -l nodes=1:ppn={{PPN}}
#PBS -l mem={{MEMORY}}gb
#PBS -N {{JOB_NAME}}

#######################################
echo "Working directory is $PBS_O_WORKDIR"

cd $PBS_O_WORKDIR

# Check your system first, your system may have different module name or different command method
module load trimmomatic/0.39-hixteqg

name={{NAME}}
num_thread={{NUM_THREAD}}

# Directories and files
data=${PBS_O_WORKDIR}/01.Rawdata/
out=${PBS_O_WORKDIR}/02.Trim_${name}
[[ -d ${out} ]] || mkdir -p ${out}

f1="${data}/${name}_1.fastq.gz"
f2="${data}/${name}_2.fastq.gz"


###################################

## Trim sequence data using trimmomatic 
/usr/bin/time -v -o ${out}/trimmomatic.time trimmomatic PE -threads ${num_thread} -phred33 "$f1" "$f2" \
    ${out}/${name}_1_paired.fq ${out}/${name}_1_unpaired.fq \
    ${out}/${name}_2_paired.fq ${out}/${name}_2_unpaired.fq \
    ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10 LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:3


##### Gzip
/usr/bin/time -v -o ${out}/zip.time pigz -v -9 \
    ${out}/${name}_1_paired.fq ${out}/${name}_1_unpaired.fq \
    ${out}/${name}_2_paired.fq ${out}/${name}_2_unpaired.fq






#### Quality check on unmapped reads

/usr/bin/time -v -o ${OutQC}/${name}_fastqc.time fastqc ${out}/${name}_1_paired.fq.gz ${out}/${name}_2_paired.fq.gz -o "${OutQC}" -t 2

echo "All done on $(date)"



##### create tsv from html

## First time only (create conda environment)
# conda env remove -n dashboard --yes
# conda create -n dashboard python=3.11
# conda activate dashboard
# conda install -c pandas pillow


# Check your system first, your system may have different module name or different command method
module load conda3/4.9.2

conda activate dashboard

########### strand 1 ###########

OutQC=${out}/QC
[[ -d ${OutQC} ]] || mkdir -p ${OutQC}
OutQC_tsv=${out}/QC_tsv_1
[[ -d ${OutQC_tsv} ]] || mkdir -p ${OutQC_tsv}
output_dir=${OutQC_tsv}/Visualize_QC
[[ -d ${output_dir} ]] || mkdir -p ${output_dir}

file_path=${OutQC}/${name}_1_paired_fastqc.html
tsv_path=${OutQC_tsv}/original_fastqc_paired_1_summary.tsv
tsv_edit_path=${OutQC_tsv}/fastqc_paired_1_summary.tsv

# QC_html --> QC_tsv
python ${PBS_O_WORKDIR}/dashboard/extract_html.py $file_path $tsv_path $output_dir

# edit tsv file
python ${PBS_O_WORKDIR}/dashboard/edit_tsv.py $tsv_path $tsv_edit_path

# QC_tsv --> NICE_QC_tsv
formatted_tsv_path=${OutQC_tsv}/NICE_fastqc_paired_1_summary.txt

python ${PBS_O_WORKDIR}/dashboard/tsv_table.py $tsv_edit_path $formatted_tsv_path


########### strand 2 ###########

OutQC=${out}/QC
[[ -d ${OutQC} ]] || mkdir -p ${OutQC}
OutQC_tsv=${out}/QC_tsv_2
[[ -d ${OutQC_tsv} ]] || mkdir -p ${OutQC_tsv}
output_dir=${OutQC_tsv}/Visualize_QC
[[ -d ${output_dir} ]] || mkdir -p ${output_dir}

file_path=${OutQC}/${name}_2_paired_fastqc.html
tsv_path=${OutQC_tsv}/original_fastqc_paired_2_summary.tsv
tsv_edit_path=${OutQC_tsv}/fastqc_paired_2_summary.tsv

# QC_html --> QC_tsv
python ${PBS_O_WORKDIR}/dashboard/extract_html.py $file_path $tsv_path $output_dir

# edit tsv file
python ${PBS_O_WORKDIR}/dashboard/edit_tsv.py $tsv_path $tsv_edit_path

# QC_tsv --> NICE_QC_tsv
formatted_tsv_path=${OutQC_tsv}/NICE_fastqc_paired_2_summary.txt

python ${PBS_O_WORKDIR}/dashboard/tsv_table.py $tsv_edit_path $formatted_tsv_path


conda deactivate
