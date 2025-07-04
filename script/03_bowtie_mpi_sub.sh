### Declare job non-rerunable 
#PBS -r n
### Output files
#PBS -e parallel.err
#PBS -o parallel.log
#PBS -l walltime={{TIME}}
#PBS -l nodes=1:ppn={{PPN}}
#PBS -l mem={{MEMORY}}gb
#PBS -N {{JOB_NAME}}

echo "Working directory is $PBS_O_WORKDIR"
cd $PBS_O_WORKDIR

# Check your system first, your system may have different module name or different command method
module load bio/Bowtie2
module load fastqc/0.11.9-4l7p7rb
module load gnu9/9.3.0
module load openmpi4/4.0.4

########################################################################

name={{NAME}}
NPROCS={{NUM_PROC}}
THREADS_PER_PROC={{NUM_THREAD}}

########################################################################

# Directories and files
out="$PBS_O_WORKDIR/02.Trim_${name}"
GENOME_DIR="$PBS_O_WORKDIR/ref_genome/ref_${name}"

OUT_DIR=${PBS_O_WORKDIR}/"03.Mapping-genome-bowtie_MPI_${name}"
[[ -d ${OUT_DIR} ]] || mkdir -p ${OUT_DIR}



#####################################



OUT_DIR_UNMAP=${OUT_DIR}/"unmapped_temp"
[[ -d ${OUT_DIR_UNMAP} ]] || mkdir -p ${OUT_DIR_UNMAP}

OutResult=${OUT_DIR}/Unmapped_reads
[[ -d ${OutResult} ]] || mkdir -p ${OutResult}

# QC_html
OutQC=${OUT_DIR}/QC
[[ -d ${OutQC} ]] || mkdir -p ${OutQC}

cd $OUT_DIR








# Extracted ref genome name
for file_path in ${GENOME_DIR}/*.fna.gz; 

do
    [ -e "$file_path" ] || { echo "No files found matching pattern *.fna.gz"; exit 1; }
    
    filename=$(basename "$file_path")
    GENOME_NAME_noPath=$(basename "$filename" ".fna.gz")
    
    GENOME=${file_path}
    GENOME_NAME=${GENOME%.fna.gz}
    echo "Extracted Ref genome Name: $GENOME_NAME_noPath"
    break
done





# Extracted Sample Name
for file_path in ${out}/*_1_paired.fq.gz; 

do
    [ -e "$file_path" ] || { echo "No files found matching pattern *_1_paired.fq.gz"; exit 1; }
    
    filename=$(basename "$file_path")
    
    sample_name=$(basename "$filename" "_1_paired.fq.gz")
    echo "Extracted Sample Name: $sample_name"

    SAMPLE_NAME=$sample_name
    break

done



F1="${out}/${SAMPLE_NAME}_1_paired.fq.gz"
F2="${out}/${SAMPLE_NAME}_2_paired.fq.gz"

#########################################################

cd $GENOME_DIR

if ! ls ${GENOME_NAME}*.bt* 1> /dev/null 2>&1; then
   echo "Indexing genome as ${GENOME_NAME}..."
   /usr/bin/time -v -o ${OUT_DIR}/indexing.time bowtie2-build --large-index --threads ${NPROCS} "${GENOME}" "${GENOME_NAME}" &> ${OUT_DIR}/indexing-genome.log
else
   echo "Indexing already present. Skipping..."
fi

echo "Processing Sample ${SAMPLE_NAME} on $(date)"

cd $OUT_DIR


### Splitting

# Determine SPLIT_LINES based on total lines and desired number of subsets.
total_lines=$(zcat ${F1} | wc -l)
lines_per_part=$((total_lines / NPROCS))

# Ensure lines are divisible by 4
SPLIT_LINES=$((lines_per_part - (lines_per_part % 4)))

echo "Total lines in ${F1}: ${total_lines}"
echo "Splitting into ${NPROCS} parts, each with ${SPLIT_LINES} lines."

# Temporary directory for splitted files
SPLIT_DIR="${OUT_DIR}/${SAMPLE_NAME}_split"
[[ -d ${SPLIT_DIR} ]] && rm -rf ${SPLIT_DIR}
mkdir -p ${SPLIT_DIR}

# Split files
/usr/bin/time -v -o split.time bash -c "
zcat ${F1} | split -d -l ${SPLIT_LINES} - ${SPLIT_DIR}/${SAMPLE_NAME}_1_
zcat ${F2} | split -d -l ${SPLIT_LINES} - ${SPLIT_DIR}/${SAMPLE_NAME}_2_
"

# Check if we have more than NPROCS chunks
f1_chunks=( ${SPLIT_DIR}/${SAMPLE_NAME}_1_* )
f2_chunks=( ${SPLIT_DIR}/${SAMPLE_NAME}_2_* )

num_f1_chunks=${#f1_chunks[@]}
num_f2_chunks=${#f2_chunks[@]}

if [ $num_f1_chunks -gt $NPROCS ] || [ $num_f2_chunks -gt $NPROCS ]; then
    # If we have an extra chunk, merge it into the last chunk. 
    # The extra chuck is very small, number of reads fewer than N, compared to other chunks.
    # For example, if we have chunks _00 to _07 plus an _08, append _08 to _07 and remove _08.

    last_index=$(printf "%02d" $((NPROCS-1)))
    extra_index=$(printf "%02d" $((NPROCS)))

    extra_f1="${SPLIT_DIR}/${SAMPLE_NAME}_1_${extra_index}"
    extra_f2="${SPLIT_DIR}/${SAMPLE_NAME}_2_${extra_index}"
    last_f1="${SPLIT_DIR}/${SAMPLE_NAME}_1_${last_index}"
    last_f2="${SPLIT_DIR}/${SAMPLE_NAME}_2_${last_index}"

    if [ -f "$extra_f1" ]; then
        cat "$extra_f1" >> "$last_f1"
        rm "$extra_f1"
    fi

    if [ -f "$extra_f2" ]; then
        cat "$extra_f2" >> "$last_f2"
        rm "$extra_f2"
    fi
fi

ls ${SPLIT_DIR}/${SAMPLE_NAME}_1_* | sort > ${SPLIT_DIR}/f1_list.txt
ls ${SPLIT_DIR}/${SAMPLE_NAME}_2_* | sort > ${SPLIT_DIR}/f2_list.txt

paste ${SPLIT_DIR}/f1_list.txt ${SPLIT_DIR}/f2_list.txt > ${SPLIT_DIR}/pairs_list.txt

### MPI script to run bowtie2 on each chunk
MPI_SCRIPT=${SPLIT_DIR}/mpi_bowtie2.sh
cat << 'EOF' > $MPI_SCRIPT
#!/usr/bin/env bash
# We do not need SAM output, only unmapped reads.
# Arguments:
# 1: pairs_list
# 2: GENOME_NAME
# 3: THREADS_PER_PROC
# 4: OUT_DIR_UNMAP
# 5: SAMPLE_NAME

pairs_list=$1
genome_name=$2
threads=$3
out_unmap=$4
sample=$5

RANK=${OMPI_COMM_WORLD_RANK:-0}
line=$(sed -n "$((RANK+1))p" $pairs_list)
f1=$(echo $line | awk '{print $1}')
f2=$(echo $line | awk '{print $2}')

chunk_id=$(basename $f1 | sed 's/^.*_1_//')

unmap_prefix="${out_unmap}/${sample}_${chunk_id}_unmap_genome.fq"

bowtie2 -p ${threads} -x ${genome_name} -1 $f1 -2 $f2 --un-conc ${unmap_prefix} -S /dev/null
EOF

chmod +x $MPI_SCRIPT

### Run MPI mapping
/usr/bin/time -v -o mpi_mapping.time mpirun -np ${NPROCS} \
   bash $MPI_SCRIPT \
   ${SPLIT_DIR}/pairs_list.txt \
   ${GENOME_NAME} \
   ${THREADS_PER_PROC} \
   ${OUT_DIR_UNMAP} \
   ${SAMPLE_NAME}


### Merge unmapped reads into final outputs

ls ${OUT_DIR_UNMAP}/${SAMPLE_NAME}_*_unmap_genome.1.fq | sort > ${SPLIT_DIR}/unmap_1_list.txt
ls ${OUT_DIR_UNMAP}/${SAMPLE_NAME}_*_unmap_genome.2.fq | sort > ${SPLIT_DIR}/unmap_2_list.txt

/usr/bin/time -v -o merge_unmapped.time bash -c "
cat \$(cat ${SPLIT_DIR}/unmap_1_list.txt) > ${OutResult}/${SAMPLE_NAME}_unmap_genome.1.fq
cat \$(cat ${SPLIT_DIR}/unmap_2_list.txt) > ${OutResult}/${SAMPLE_NAME}_unmap_genome.2.fq
"



#### Quality check on unmapped reads

/usr/bin/time -v -o ${OutQC}/fastqc.time fastqc ${OutResult}/${SAMPLE_NAME}_unmap_genome.1.fq ${OutResult}/${SAMPLE_NAME}_unmap_genome.2.fq -o "${OutQC}" -t 2

echo "All done on $(date)"


# Gzip file (pigz -v -9 -k , if you want to keep the original result)
/usr/bin/time -v -o ${OUT_DIR}/zip.time pigz -v -9 ${OutResult}/${SAMPLE_NAME}_unmap_genome.1.fq ${OutResult}/${SAMPLE_NAME}_unmap_genome.2.fq


rm -rf ${OUT_DIR}/${SAMPLE_NAME}_split
rm -rf ${OUT_DIR_UNMAP}



##### create tsv from html

## First time only (create conda environment)
# conda env remove -n dashboard --yes
# conda create -n dashboard python=3.11
# conda activate dashboard
# conda install -c pandas pillow

module load conda3/4.9.2

conda activate dashboard

########### strand 1 ###########

# make QC_html --> QC_TSV
OutQC_tsv=${OUT_DIR}/QC_tsv_1
[[ -d ${OutQC_tsv} ]] || mkdir -p ${OutQC_tsv}

file_path=${OutQC}/${SAMPLE_NAME}_unmap_genome.1_fastqc.html
tsv_path=${OutQC_tsv}/original_${SAMPLE_NAME}_unmap_genome.1_fastqc_summary.tsv
tsv_edit_path=${OutQC_tsv}/${SAMPLE_NAME}_unmap_genome.1_fastqc_summary.tsv

output_dir=${OutQC_tsv}/Visualize_QC
[[ -d ${output_dir} ]] || mkdir -p ${output_dir}

# QC_html --> QC_tsv
python ${PBS_O_WORKDIR}/dashboard/extract_html.py $file_path $tsv_path $output_dir

# edit tsv file
python ${PBS_O_WORKDIR}/dashboard/edit_tsv.py $tsv_path $tsv_edit_path

# QC_tsv --> NICE_QC_tsv
formatted_tsv_path=${OutQC_tsv}/NICE_${SAMPLE_NAME}_unmap_genome.1_fastqc_summary.txt

python ${PBS_O_WORKDIR}/dashboard/tsv_table.py $tsv_edit_path $formatted_tsv_path


########### strand 2 ###########

# make QC_html --> QC_TSV
OutQC_tsv=${OUT_DIR}/QC_tsv_2
[[ -d ${OutQC_tsv} ]] || mkdir -p ${OutQC_tsv}

file_path=${OutQC}/${SAMPLE_NAME}_unmap_genome.2_fastqc.html
tsv_path=${OutQC_tsv}/original_${SAMPLE_NAME}_unmap_genome.2_fastqc_summary.tsv
tsv_edit_path=${OutQC_tsv}/${SAMPLE_NAME}_unmap_genome.2_fastqc_summary.tsv

output_dir=${OutQC_tsv}/Visualize_QC
[[ -d ${output_dir} ]] || mkdir -p ${output_dir}

# QC_html --> QC_tsv
python ${PBS_O_WORKDIR}/dashboard/extract_html.py $file_path $tsv_path $output_dir

# edit tsv file
python ${PBS_O_WORKDIR}/dashboard/edit_tsv.py $tsv_path $tsv_edit_path

# QC_tsv --> NICE_QC_tsv
formatted_tsv_path=${OutQC_tsv}/NICE_${SAMPLE_NAME}_unmap_genome.2_fastqc_summary.txt

python ${PBS_O_WORKDIR}/dashboard/tsv_table.py $tsv_edit_path $formatted_tsv_path


conda deactivate


