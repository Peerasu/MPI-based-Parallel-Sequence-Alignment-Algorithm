### Declare job non-rerunable 
#PBS -r n
### Output files
#PBS -e parallel.err
#PBS -o parallel.log
#PBS -l walltime=24:00:00
#PBS -l nodes=1:ppn=32
#PBS -l mem=250gb

#PBS -N Bowtie2_ORIGINAL_250gb_32ppn_128p

#######################################
echo Working directory is $PBS_O_WORKDIR 

cd $PBS_O_WORKDIR

# Check your system first, your system may have different module name or different command method
module load bio/Bowtie2
module load fastqc/0.11.9-4l7p7rb


###################################

name="SRR9733638"    # SRR9733638  SRR9733640  SRR23958681  SRR7789809  SRR7789808   

###################################

# Directories and files
out="$PBS_O_WORKDIR/02.Trim_${name}"
GENOME_DIR="$PBS_O_WORKDIR/ref_genome/ref_${name}"

OUT_DIR=${PBS_O_WORKDIR}/"03.Mapping-genome-bowtie_${name}"
[[ -d ${OUT_DIR} ]] || mkdir -p ${OUT_DIR}

OUT_DIR_UNMAP=${OUT_DIR}/"Unmapped_reads"
[[ -d ${OUT_DIR_UNMAP} ]] || mkdir -p ${OUT_DIR_UNMAP}

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

echo "GENOME: ${GENOME}"
echo "GENOME_NAME: ${GENOME_NAME}"
echo "GENOME_NAME_noPath: ${GENOME_NAME_noPath}"




#########################################################

cd $GENOME_DIR

if ! ls ${GENOME_NAME}*.bt* 1> /dev/null 2>&1; then
   echo "Indexing genome as ${GENOME_NAME}"
   /usr/bin/time -v -o ${OUT_DIR}/indexing.time bowtie2-build --large-index --threads 32 "${GENOME}" "${GENOME_NAME}" &> ${OUT_DIR}/indexing-genome.log
else
   echo "Indexing already present. Skipping..."
fi

echo "Bowtie Indexing Sample ${SAMPLE_NAME} on $(date)"

cd $OUT_DIR



##Mapping

/usr/bin/time -v -o ${OUT_DIR}/mapping.time \ 
bowtie2 -p 128 -x ${GENOME_NAME} -1 $F1 -2 $F2 --un-conc-gz ${OUT_DIR_UNMAP}/${SAMPLE_NAME}_unmap_genome.fq.gz -S /dev/null

# rm *sam

echo "All sample done on" `date`  





##Quality check

OutQC=${OUT_DIR_UNMAP}/QC
[[ -d ${OutQC} ]] || mkdir -p ${OutQC}

/usr/bin/time -v -o ${OUT_DIR}/fastqc.time fastqc ${OUT_DIR_UNMAP}/${SAMPLE_NAME}_unmap_genome.fq.1.gz ${OUT_DIR_UNMAP}/${SAMPLE_NAME}_unmap_genome.fq.2.gz -o "${OutQC}" -t 2



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

# make QC_html --> QC_TSV
OutQC_tsv=${OUT_DIR}/QC_tsv_1
[[ -d ${OutQC_tsv} ]] || mkdir -p ${OutQC_tsv}

file_path=${OutQC}/${SAMPLE_NAME}_unmap_genome.fq.1_fastqc.html
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

file_path=${OutQC}/${SAMPLE_NAME}_unmap_genome.fq.2_fastqc.html
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




