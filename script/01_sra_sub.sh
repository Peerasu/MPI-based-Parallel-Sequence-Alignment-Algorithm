### Declare job non-rerunable 
#PBS -r n
### Output files
#PBS -e parallel.err
#PBS -o parallel.log
### Mail to user
#PBS -m ae
#PBS -l walltime={{TIME}}
#PBS -l nodes=1:ppn={{PPN}}
#PBS -l mem={{MEMORY}}gb
#PBS -N {{JOB_NAME}}

#######################################
echo Working directory is $PBS_O_WORKDIR 

cd $PBS_O_WORKDIR

srr={{NAME}}
# srr="SRR23958655"

###########################

# Directories and files
OUT_DIR=${PBS_O_WORKDIR}/01.Rawdata
[[ -d ${OUT_DIR} ]] || mkdir -p ${OUT_DIR}

OutQC=${OUT_DIR}/QC
[[ -d ${OutQC} ]] || mkdir -p ${OutQC}

cd $OUT_DIR

for i in $srr;
do 	

/usr/bin/time -v -o ${OUT_DIR}/${srr}_load.time /share/data/home/peerasu.p/sratoolkit.3.1.1-centos_linux64/bin/fasterq-dump --split-files --include-technical $i

done

mv *.gz $OUT_DIR 2>srr.err  




#### Quality check on unmapped reads

/usr/bin/time -v -o ${OutQC}/${srr}_fastqc.time fastqc ${srr}_1.fastq ${srr}_2.fastq -o "${OutQC}" -t 2

echo "All done on $(date)"


# Gzip file (pigz -v -9 -k , if you want to keep the original result)
/usr/bin/time -v -o ${OUT_DIR}/${srr}_zip.time pigz -v -9 ${srr}_1.fastq ${srr}_2.fastq



##### create tsv from html

## First time only (create conda environment)
# conda env remove -n dashboard --yes
# conda create -n dashboard python=3.11
# conda activate dashboard
# conda install -c pandas pillow

module load conda3/4.9.2

conda activate dashboard

########### strand 1 ###########

OutQC_tsv=${OUT_DIR}/QC_tsv_1_${srr}
[[ -d ${OutQC_tsv} ]] || mkdir -p ${OutQC_tsv}

file_path=${OutQC}/${srr}_1_fastqc.html
tsv_path=${OutQC_tsv}/original_fastqc_1_summary.tsv
tsv_edit_path=${OutQC_tsv}/fastqc_1_summary.tsv

output_dir=${OutQC_tsv}/Visualize_QC
[[ -d ${output_dir} ]] || mkdir -p ${output_dir}

# QC_html --> QC_tsv
python ${PBS_O_WORKDIR}/dashboard/extract_html.py $file_path $tsv_path $output_dir


# edit tsv file
python ${PBS_O_WORKDIR}/dashboard/edit_tsv.py $tsv_path $tsv_edit_path


# QC_tsv --> NICE_QC_tsv
formatted_tsv_path=${OutQC_tsv}/NICE_fastqc_1_summary.txt

python ${PBS_O_WORKDIR}/dashboard/tsv_table.py $tsv_edit_path $formatted_tsv_path


########### strand 2 ###########

OutQC_tsv=${OUT_DIR}/QC_tsv_2_${srr}
[[ -d ${OutQC_tsv} ]] || mkdir -p ${OutQC_tsv}

file_path=${OutQC}/${srr}_2_fastqc.html
tsv_path=${OutQC_tsv}/original_fastqc_2_summary.tsv
tsv_edit_path=${OutQC_tsv}/fastqc_2_summary.tsv

output_dir=${OutQC_tsv}/Visualize_QC
[[ -d ${output_dir} ]] || mkdir -p ${output_dir}

# QC_html --> QC_tsv
python ${PBS_O_WORKDIR}/dashboard/extract_html.py $file_path $tsv_path $output_dir


# edit tsv file
python ${PBS_O_WORKDIR}/dashboard/edit_tsv.py $tsv_path $tsv_edit_path


# QC_tsv --> NICE_QC_tsv
formatted_tsv_path=${OutQC_tsv}/NICE_fastqc_2_summary.txt

python ${PBS_O_WORKDIR}/dashboard/tsv_table.py $tsv_edit_path $formatted_tsv_path



conda deactivate


