#!/bin/bash

set -e


################################# User input #################################

# Define parameter arrays
names=(SRR23958681 SRR23958667 SRR23958665)             # Sample names
memories=(80 80 80)                                     # Memory in GB
times=("10:00:00" "80:00:00" "80:00:00")                # Walltime
ppns=(16 16 16)                                         # Processors per node

############################################################################## 


JOB_NAME_PREFIX="Rawdata"
TEMPLATE="$HOME/script/01_sra_sub.sh"

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

    JOB_NAME="${JOB_NAME_PREFIX}_${name}"
    JOB_SCRIPT="$HOME/script/01_sra_sub_${name}.sh"

    sed -e "s/{{TIME}}/${time}/" \
        -e "s/{{PPN}}/${ppn}/" \
        -e "s/{{MEMORY}}/${memory}/" \
        -e "s/{{JOB_NAME}}/${JOB_NAME}/" \
        -e "s/{{NAME}}/${name}/" \
        "$TEMPLATE" > "$JOB_SCRIPT"

    qsub "$JOB_SCRIPT"

    echo "Submitted job: $JOB_NAME with memory=${memory}gb, time=${time}, ppn=${ppn}"

    rm -rf $JOB_SCRIPT
done
