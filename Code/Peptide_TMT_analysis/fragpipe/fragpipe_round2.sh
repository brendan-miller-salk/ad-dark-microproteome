#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --partition=epyc-64
#SBATCH --account=hassy_472
#SBATCH --cpus-per-task=6
#SBATCH --time=6:00:00
#SBATCH --mem-per-cpu=24GB
#SBATCH --job-name="b${SLURM_ARRAY_TASK_ID}_tmt_round2_rescore"
#SBATCH --mail-type=END
#SBATCH --array=6-8

# Delay the start of each job based on the SLURM_ARRAY_TASK_ID (e.g., 10 seconds per task ID)
DELAY=$((SLURM_ARRAY_TASK_ID * 5))
echo "Delaying start by $DELAY seconds"
sleep $DELAY

module load openjdk

export PATH=$PATH:/scratch1/brendajm/tools/fragpipe/bin

# Define the base directory
BASE_DIR="/scratch1/brendajm/tmt_rosmap/round2"

# Construct the specific directory for this array task
DIR="${BASE_DIR}/b${SLURM_ARRAY_TASK_ID}"

# Set the output file
OUTPUT_FILE="${DIR}/b${SLURM_ARRAY_TASK_ID}_tmt.out"

# Create annotation content dynamically based on SLURM_ARRAY_TASK_ID
ANNOTATION_CONTENT=$(cat << EOF
126     b${SLURM_ARRAY_TASK_ID}.126
127N    b${SLURM_ARRAY_TASK_ID}.127N
127C    b${SLURM_ARRAY_TASK_ID}.127C
128N    b${SLURM_ARRAY_TASK_ID}.128N
128C    b${SLURM_ARRAY_TASK_ID}.128C
129N    b${SLURM_ARRAY_TASK_ID}.129N
129C    b${SLURM_ARRAY_TASK_ID}.129C
130N    b${SLURM_ARRAY_TASK_ID}.130N
130C    b${SLURM_ARRAY_TASK_ID}.130C
131N    b${SLURM_ARRAY_TASK_ID}.131N
131C    b${SLURM_ARRAY_TASK_ID}.131C
132N    b${SLURM_ARRAY_TASK_ID}.132N
132C    b${SLURM_ARRAY_TASK_ID}.132C
133N    b${SLURM_ARRAY_TASK_ID}.133N
133C    b${SLURM_ARRAY_TASK_ID}.133C
134N    b${SLURM_ARRAY_TASK_ID}.134N
EOF
)

# Check if the directory exists
if [ -d "$DIR" ]; then
  # Create annotation.txt file
  echo "$ANNOTATION_CONTENT" > "${DIR}/annotation.txt"

  # Remove the manifest file if it exists
  rm -f "${DIR}/b${SLURM_ARRAY_TASK_ID}.manifest"

  # Create a new manifest file
  for file in "${DIR}"/*b${SLURM_ARRAY_TASK_ID}*mzML; do
    echo "${file}"$'\t'"DDA" >> "${DIR}/b${SLURM_ARRAY_TASK_ID}.manifest"
  done

  # Check if the shortstop_proteogenomics_appended_results_cpm05 directory exists, create it if it doesn't
  if [ ! -d "${DIR}/shortstop_proteogenomics_appended_results_cpm05" ]; then
    mkdir "${DIR}/shortstop_proteogenomics_appended_results_cpm05"
  fi

  # Check to make sure shortstop_proteogenomics_appended_results_cpm05 directory is empty and delete everything in it if it's not
  if [ "$(ls -A "${DIR}/shortstop_proteogenomics_appended_results_cpm05")" ]; then
    rm -rf "${DIR}/shortstop_proteogenomics_appended_results_cpm05"/*
  fi

  cp "${BASE_DIR}/fragpipe_processing_files/tmt_shortstop_proteogenomics_appended.workflow" "${DIR}"

  # Run fragpipe with the specified parameters
  fragpipe --headless \
    --workflow "${DIR}/tmt_shortstop_proteogenomics_appended.workflow" \
    --manifest "${DIR}/b${SLURM_ARRAY_TASK_ID}.manifest" \
    --workdir "${DIR}/shortstop_proteogenomics_appended_results_cpm05" \
    --config-tools-folder /scratch1/brendajm/tools/ \
    --config-python /apps/spack/2406/apps/linux-rocky8-x86_64_v3/gcc-13.3.0/python-3.11.9-x74mtjf/bin/python
else
  echo "Directory $DIR does not exist." &> "$OUTPUT_FILE"
fi
