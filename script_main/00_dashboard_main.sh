#!/bin/bash

set -e


################################# User input #################################

names=(SRR23958655 SRR23958656 SRR23958665)

##############################################################################





####################################### # This job's working directory

PBS_O_WORKDIR=/share/data/home/"$USER"

echo Working directory is $PBS_O_WORKDIR 

# Check your system first, your system may have different module name or different command method
module load conda3/4.9.2

cd $PBS_O_WORKDIR


for name in ${names[@]};
do 	

    echo "##############################   Creating Dashboard for $name .....   ##############################"

    Rawdata_dir="$PBS_O_WORKDIR/01.Rawdata"
    Trim_dir="$PBS_O_WORKDIR/02.Trim_${name}"
    Bowtie_dir="$PBS_O_WORKDIR/03.Mapping-genome-bowtie_MPI_${name}"
    Assembly_dir="$PBS_O_WORKDIR/05.assembly_${name}"

    ###########################

    Rawdata_1_qc="${Rawdata_dir}/QC_tsv_1_${name}"
    Trim_1_qc="${Trim_dir}/QC_tsv_1"
    Bowtie_1_qc="${Bowtie_dir}/QC_tsv_1"

    Rawdata_2_qc="${Rawdata_dir}/QC_tsv_2_${name}"
    Trim_2_qc="${Trim_dir}/QC_tsv_2"
    Bowtie_2_qc="${Bowtie_dir}/QC_tsv_2"

    Assembly_qc="${Assembly_dir}/dashboard/assembly"
    Binning_qc="${Assembly_dir}/dashboard/binning"



    ###########################



    conda activate dashboard

    Dashboard_files="${PBS_O_WORKDIR}/dashboard_files_${name}"

    Raw_1_dash=${Dashboard_files}/Rawdata-1
    Trim_1_dash=${Dashboard_files}/Trimming-1
    Bowtie_1_dash=${Dashboard_files}/Alignment-1

    Raw_2_dash=${Dashboard_files}/Rawdata-2
    Trim_2_dash=${Dashboard_files}/Trimming-2
    Bowtie_2_dash=${Dashboard_files}/Alignment-2

    Assembly_dash=${Dashboard_files}/Assembly
    Binning_dash=${Dashboard_files}/Binning

    Compare_1_dash=${Dashboard_files}/Compare-1
    Compare_2_dash=${Dashboard_files}/Compare-2

    Summary_dash=${Dashboard_files}/Summary


    # Check if dash_dir already exists. if it exists we then delete the existing dash_dir
    if [[ -d "${Dashboard_files}" ]]; then
        rm -rf ${Dashboard_files}
    fi
    if [[ -d "${Raw_1_dash}" ]]; then
        rm -rf ${Raw_1_dash}
    fi
    if [[ -d "${Trim_1_dash}" ]]; then
        rm -rf ${Trim_1_dash}
    fi
    if [[ -d "${Bowtie_1_dash}" ]]; then
        rm -rf ${Bowtie_1_dash}
    fi
    if [[ -d "${Raw_2_dash}" ]]; then
        rm -rf ${Raw_2_dash}
    fi
    if [[ -d "${Trim_2_dash}" ]]; then
        rm -rf ${Trim_2_dash}
    fi
    if [[ -d "${Bowtie_2_dash}" ]]; then
        rm -rf ${Bowtie_2_dash}
    fi
    if [[ -d "${Assembly_dash}" ]]; then
        rm -rf ${Assembly_dash}
    fi
    if [[ -d "${Binning_dash}" ]]; then
        rm -rf ${Binning_dash}
    fi
    if [[ -d "${Compare_1_dash}" ]]; then
        rm -rf ${Compare_1_dash}
    fi
    if [[ -d "${Compare_2_dash}" ]]; then
        rm -rf ${Compare_2_dash}
    fi
    if [[ -d "${Summary_dash}" ]]; then
        rm -rf ${Summary_dash}
    fi


    mkdir -p ${Dashboard_files}

    cp -R ${Rawdata_1_qc} ${Raw_1_dash}
    cp -R ${Trim_1_qc} ${Trim_1_dash} 
    cp -R ${Bowtie_1_qc} ${Bowtie_1_dash}

    cp -R ${Rawdata_2_qc} ${Raw_2_dash}
    cp -R ${Trim_2_qc} ${Trim_2_dash} 
    cp -R ${Bowtie_2_qc} ${Bowtie_2_dash}

    cp -R ${Assembly_qc} ${Assembly_dash} 
    cp -R ${Binning_qc} ${Binning_dash} 

    mkdir -p ${Compare_1_dash}
    mkdir -p ${Compare_2_dash}
    mkdir -p ${Summary_dash}


    cp ${Rawdata_dir}/QC/${name}_1_fastqc.html ${Raw_1_dash}
    cp ${Trim_dir}/QC/${name}_1*_fastqc.html ${Trim_1_dash} 
    cp ${Bowtie_dir}/QC/${name}*.1_fastqc.html ${Bowtie_1_dash}

    cp ${Rawdata_dir}/QC/${name}_2_fastqc.html ${Raw_2_dash}
    cp ${Trim_dir}/QC/${name}_2*_fastqc.html ${Trim_2_dash} 
    cp ${Bowtie_dir}/QC/${name}*.2_fastqc.html ${Bowtie_2_dash}


    rm -rf ${Raw_1_dash}/original*.tsv
    rm -rf ${Trim_1_dash}/original*.tsv
    rm -rf ${Bowtie_1_dash}/original*.tsv

    rm -rf ${Raw_2_dash}/original*.tsv
    rm -rf ${Trim_2_dash}/original*.tsv
    rm -rf ${Bowtie_2_dash}/original*.tsv


    mv ${Raw_1_dash}/fastqc_1_summary.tsv ${Raw_1_dash}/${name}_Rawdata_1.tsv
    mv ${Raw_2_dash}/fastqc_2_summary.tsv ${Raw_2_dash}/${name}_Rawdata_2.tsv
    mv ${Raw_1_dash}/NICE_fastqc_1_summary.txt ${Raw_1_dash}/${name}_NICE_Rawdata_1.txt
    mv ${Raw_2_dash}/NICE_fastqc_2_summary.txt ${Raw_2_dash}/${name}_NICE_Rawdata_2.txt

    mv ${Trim_1_dash}/fastqc_paired_1_summary.tsv ${Trim_1_dash}/${name}_Trim_1.tsv
    mv ${Trim_2_dash}/fastqc_paired_2_summary.tsv ${Trim_2_dash}/${name}_Trim_2.tsv
    mv ${Trim_1_dash}/NICE_fastqc_paired_1_summary.txt ${Trim_1_dash}/${name}_NICE_Trim_1.txt
    mv ${Trim_2_dash}/NICE_fastqc_paired_2_summary.txt ${Trim_2_dash}/${name}_NICE_Trim_2.txt

    mv ${Bowtie_1_dash}/SRR23958655_unmap_genome.1_fastqc_summary.tsv ${Bowtie_1_dash}/${name}_Alignment-1.tsv
    mv ${Bowtie_2_dash}/SRR23958655_unmap_genome.2_fastqc_summary.tsv ${Bowtie_2_dash}/${name}_Alignment-2.tsv
    mv ${Bowtie_1_dash}/NICE_SRR23958655_unmap_genome.1_fastqc_summary.txt ${Bowtie_1_dash}/${name}_NICE_Alignment-1.txt
    mv ${Bowtie_2_dash}/NICE_SRR23958655_unmap_genome.2_fastqc_summary.txt ${Bowtie_2_dash}/${name}_NICE_Alignment-2.txt

    mv ${Assembly_dash}/assembly_summary.tsv ${Assembly_dash}/${name}_Assembly.tsv
    mv ${Assembly_dash}/NICE_assembly_summary.txt ${Assembly_dash}/${name}_NICE_Assembly.txt

    mv ${Binning_dash}/checkM_summary.tsv ${Binning_dash}/${name}_Binning.tsv 
    mv ${Binning_dash}/NICE_checkM_summary.txt ${Binning_dash}/${name}_NICE_Binning.txt



    ### create compare - strand 1
    out_compare_1="${Compare_1_dash}/compare_1.tsv"
    python ${PBS_O_WORKDIR}/dashboard/compare.py $Dashboard_files $out_compare_1 1

    ### create compare - strand 2
    out_compare_2="${Compare_2_dash}/compare_2.tsv"
    python ${PBS_O_WORKDIR}/dashboard/compare.py $Dashboard_files $out_compare_2 2

    out_summary="${Summary_dash}/${name}_Summary.tsv"
    python ${PBS_O_WORKDIR}/dashboard/combine_compare.py $out_compare_1 $out_compare_2 $out_summary

    ### QC_tsv --> NICE_QC_tsv
    formatted_tsv_path="${Summary_dash}/${name}_NICE_Summary.txt"
    python ${PBS_O_WORKDIR}/dashboard/summary_table.py $out_summary $formatted_tsv_path

    rm -rf $Compare_1_dash $Compare_2_dash

    ### Generate HTML dashboard
    output_html="${Dashboard_files}/dashboard.html"
    python ${PBS_O_WORKDIR}/dashboard/create_html.py $Dashboard_files $output_html $name

    echo "HTML dashboard created at ${output_html}"

    conda deactivate

    echo "##############################   Dashboard for $name is at $Dashboard_files   ##############################"
done

