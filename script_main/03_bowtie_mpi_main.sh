#!/bin/bash

set -e


################################# User input #################################

# Define parameter arrays
names=(SRR23958655)                                  # Sample names     # SRR23958656   SRR23958655
memories=(250)                                       # Memory in GB
times=("24:00:00")                                   # Walltime
ppns=(32)                                            # Processors per node

procs=(32)
threads=(4)

############################################################################## 


JOB_NAME_PREFIX="Bowtie"
TEMPLATE="$HOME/script/03_bowtie_mpi_sub.sh"

if [ ! -f "$TEMPLATE" ]; then
    echo "Error: Template file $TEMPLATE not found."
    exit 1
fi

num_jobs=${#names[@]}

if [ ${#memories[@]} -ne $num_jobs ] || [ ${#times[@]} -ne $num_jobs ] || [ ${#ppns[@]} -ne $num_jobs ]; then
    echo "Error: All parameter arrays must have the same length."
    exit 1
fi

for (( i=0; i<num_jobs; i++ ))
do
    name=${names[$i]}
    memory=${memories[$i]}
    time=${times[$i]}
    ppn=${ppns[$i]}
    proc=${procs[$i]}
    thread=${threads[$i]}

    JOB_NAME="${JOB_NAME_PREFIX}_${name}"
    JOB_SCRIPT="$HOME/script/03_bowtie_mpi_sub_${name}.sh"

    sed -e "s/{{TIME}}/${time}/" \
        -e "s/{{PPN}}/${ppn}/" \
        -e "s/{{MEMORY}}/${memory}/" \
        -e "s/{{JOB_NAME}}/${JOB_NAME}/" \
        -e "s/{{NAME}}/${name}/" \
        -e "s/{{NUM_PROC}}/${proc}/" \
        -e "s/{{NUM_THREAD}}/${thread}/" \
        "$TEMPLATE" > "$JOB_SCRIPT"

    qsub "$JOB_SCRIPT"

    echo "Submitted job: $JOB_NAME with memory=${memory}gb, time=${time}, ppn=${ppn}, # Process=${proc}, # Thread=${thread}"

    rm -rf $JOB_SCRIPT
done
