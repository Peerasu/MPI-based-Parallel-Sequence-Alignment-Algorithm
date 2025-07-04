#PBS -r n
### Output files
#PBS -e spades.err
#PBS -o spades.log
### Mail to user
#PBS -m ae
#PBS -l walltime={{TIME}}
#PBS -l nodes=1:ppn={{PPN}}
#PBS -l mem={{MEMORY}}gb
#PBS -N {{JOB_NAME}}

#######################################
echo Working directory is $PBS_O_WORKDIR 
cd $PBS_O_WORKDIR
####################################### 

# Check your system first, your system may have different module name or different command method
module load spades/3.14.1-cqqesu6

####################################### 

name={{NAME}}
num_thread={{NUM_THREAD}}
memory={{MEMORY}}

####################################### 

export OMP_NUM_THREADS=32
echo "OMP_NUM_THREADS is (before running): $OMP_NUM_THREADS"


input_dir="03.Mapping-genome-bowtie_MPI_${name}/Unmapped_reads"
out_dir=${PBS_O_WORKDIR}/"05.assembly_${name}"
[[ -d ${out_dir} ]] || mkdir -p ${out_dir}

F1=$input_dir/*.1.fq.gz
F2=$input_dir/*.2.fq.gz

/usr/bin/time -v -o ${out_dir}/spades.time \
spades.py --pe1-1 $F1 \
--pe1-2 $F2 \
-o $out_dir \
-t ${num_thread} -m ${memory} -k 21,33,55,77 \
--meta &>spades.log



