#PBS -r n
### Output files
#PBS -e metabat.err
#PBS -o metabat.log
#PBS -l walltime={{TIME}}
#PBS -l nodes=1:ppn={{PPN}}
#PBS -l mem={{MEMORY}}gb
#PBS -N {{JOB_NAME}}

#######################################
echo "Working directory is $PBS_O_WORKDIR" 
cd "$PBS_O_WORKDIR" 
####################################### 



##############################################################################

name={{NAME}}
num_thread={{NUM_THREAD}}

##############################################################################

# Check your system first, your system may have different module name or different command method
module load conda3/4.9.2
module load bio/QUAST/5.0.2-foss-2020a-Python-3.8.2
module load bio/bbmap/38.90
module load samtools/1.10-spgkcyn
module load bedtools2/2.27.1-rz3cqpw



# Directories and files
input_dir="${PBS_O_WORKDIR}/03.Mapping-genome-bowtie_MPI_${name}/Unmapped_reads"
assembly_dir="${PBS_O_WORKDIR}/05.assembly_${name}"
contigs="${assembly_dir}/scaffolds.fasta"

out_dir="${assembly_dir}/06.coverage"
[[ -d "${out_dir}" ]] || mkdir -p "${out_dir}"
out_dir_time="${out_dir}/time"
[[ -d "${out_dir_time}" ]] || mkdir -p "${out_dir_time}"
out_dir_log="${out_dir}/log"
[[ -d "${out_dir_log}" ]] || mkdir -p "${out_dir_log}"



############################
# Extracted Sample Name
for file_path in ${input_dir}/*.1.fq.gz; 

do
    [ -e "$file_path" ] || { echo "No files found matching pattern *.1.fq.gz"; exit 1; }
    
    filename=$(basename "$file_path")
    
    sample_name=$(basename "$filename" ".1.fq.gz")
    echo "Extracted Sample Name: $sample_name"

    SAMPLE_NAME=$sample_name
    break

done

F1="${input_dir}/${SAMPLE_NAME}.1.fq.gz"
F2="${input_dir}/${SAMPLE_NAME}.2.fq.gz"


#######################################################################
# QC scaffolds
/usr/bin/time -v -o "${out_dir_time}/quast.time" \
quast -o "$out_dir" "$contigs"

# BBMap
/usr/bin/time -v -o "${out_dir_time}/bbmap.time" \
bbmap.sh ref="${contigs}" nodisk in="$F1" in2="$F2" \
out="${out_dir}/scaffolds.bbmap.bam" \
k=15 minid=0.9 threads=32 build=1 &> ${out_dir_log}/bbmap.log

# Samtools
/usr/bin/time -v -o "${out_dir_time}/samtools.time" \
samtools sort "${out_dir}/scaffolds.bbmap.bam" -o "${out_dir}/scaffolds_sorted.bam" -@ ${num_thread} &> ${out_dir_log}/samtools.log

# Bedtools
/usr/bin/time -v -o "${out_dir_time}/bamToBed.time" \
bamToBed -i "${out_dir}/scaffolds_sorted.bam" > "${out_dir}/scaffolds_sorted.bed" &> ${out_dir_log}/b2b.log


## Binning
#############################################################
# Trim contigs

##### First time only (create conda environment)
# conda env remove -n metabat --yes
# conda create -n metabat python=3.8
# conda activate metabat
# conda install -c bioconda metabat2

conda activate metabat

bam="${out_dir}/scaffolds_sorted.bam"
out_bin="${assembly_dir}/07.binning"
[[ -d "${out_bin}" ]] || mkdir -p "${out_bin}"

out_bin_log="${out_bin}/log"
[[ -d "${out_bin_log}" ]] || mkdir -p "${out_bin_log}"

out_bin_time="${out_bin}/time"
[[ -d "${out_bin_time}" ]] || mkdir -p "${out_bin_time}"

trim="${out_bin}/trimmed_scaffolds2000.fasta"

/usr/bin/time -v -o "${out_bin_time}/reformat.time" \
reformat.sh in="$contigs" out="$trim" minlength=2000 &> ${out_bin_log}/reformat.log

/usr/bin/time -v -o "${out_bin_time}/jgi.time" \
jgi_summarize_bam_contig_depths --outputDepth "${out_bin}/s_depth.txt" "$bam" &> ${out_bin_log}/jgi.log

/usr/bin/time -v -o "${out_bin_time}/metabat.time" \
metabat -i "$trim" -t ${num_thread} \
-a "${out_bin}/s_depth.txt" \
-o "${out_bin}/Mag.bins" &> ${out_bin_log}/metabat.log

conda deactivate





##### create tsv from html

## First time only (create conda environment)
# conda env remove -n dashboard --yes
# conda create -n dashboard python=3.11
# conda activate dashboard
# conda install -c pandas pillow


conda activate dashboard

OutQC_tsv="${assembly_dir}/dashboard/assembly"
[[ -d "${OutQC_tsv}" ]] || mkdir -p "${OutQC_tsv}"

# edit coverage table
tsv_path="${out_dir}/report.tsv"
tsv_edit_path="${OutQC_tsv}/edit_report.tsv"

python ${PBS_O_WORKDIR}/dashboard/edit_tsv_assembly.py $tsv_path $tsv_edit_path

formatted_tsv_path=${OutQC_tsv}/NICE_assembly_summary.txt

python ${PBS_O_WORKDIR}/dashboard/assembly_table.py $tsv_edit_path $formatted_tsv_path

conda deactivate

mv ${OutQC_tsv}/edit_report.tsv ${OutQC_tsv}/assembly_summary.tsv




## CheckM
#######################################

# Check your system first, your system may have different module name or different command method
module purge
module load conda3/4.9.2


##### First time only (create conda environment)
# conda env remove -n checkm --yes
# conda create -n checkm python=3.7
# conda activate checkm
# conda install -c bioconda numpy matplotlib pysam
# conda install -c bioconda hmmer prodigal pplacer
# conda install -c bioconda checkm-genome


conda activate checkm

input_dir="${PBS_O_WORKDIR}/03.Mapping-genome-bowtie_MPI_${name}/Unmapped_reads"
assembly_dir="${PBS_O_WORKDIR}/05.assembly_${name}"

out_bin="${assembly_dir}/07.binning"

out_checkM="${assembly_dir}/08.checkM"
[[ -d "${out_checkM}" ]] || mkdir -p "${out_checkM}"

out_checkM_time="${out_checkM}/time"
[[ -d "${out_checkM_time}" ]] || mkdir -p "${out_checkM_time}"

out_checkM_log="${out_checkM}/log"
[[ -d "${out_checkM_log}" ]] || mkdir -p "${out_checkM_log}"

file_name="${name}-genome-bin-QC.tsv"

/usr/bin/time -v -o "${out_checkM_time}/checkM.time" \
checkm lineage_wf -t 32 -x fa --file ${out_checkM}/${file_name} --tab_table "$out_bin" "$out_checkM" &> ${out_checkM_log}/checkM.log

conda deactivate




##### create tsv from html

## First time only (create conda environment)
# conda env remove -n dashboard --yes
# conda create -n dashboard python=3.11
# conda activate dashboard
# conda install -c pandas pillow

conda activate dashboard

OutQC_tsv="${assembly_dir}/dashboard/binning"
[[ -d "${OutQC_tsv}" ]] || mkdir -p "${OutQC_tsv}"

tsv_path=${out_checkM}/${file_name}
tsv_shift_path=${out_checkM}/shift_${file_name}
tsv_sort_path=${out_checkM}/sort_${file_name}
formatted_tsv_path=${OutQC_tsv}/NICE_checkM_summary.txt

python ${PBS_O_WORKDIR}/dashboard/shift_column.py $tsv_path $tsv_shift_path

python ${PBS_O_WORKDIR}/dashboard/edit_tsv_binning.py $tsv_shift_path $tsv_sort_path

# coverage_tsv --> NICE_coverage_tsv
python ${PBS_O_WORKDIR}/dashboard/checkM_table.py $tsv_sort_path $formatted_tsv_path

conda deactivate


cp $tsv_sort_path $OutQC_tsv
mv ${OutQC_tsv}/sort_${file_name} ${OutQC_tsv}/checkM_summary.tsv