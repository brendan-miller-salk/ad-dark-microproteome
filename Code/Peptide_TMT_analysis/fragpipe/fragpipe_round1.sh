#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --partition=epyc-64
#SBATCH --account=hassy_472
#SBATCH --cpus-per-task=10
#SBATCH --time=5:00:00
#SBATCH --mem-per-cpu=24GB
#SBATCH --job-name="b${SLURM_ARRAY_TASK_ID}_tmt"
#SBATCH --mail-type=END
#SBATCH --array=4,6-10,12-50
# All files 4,6-10,12-50

# Delay the start of each job based on the SLURM_ARRAY_TASK_ID (e.g., 10 seconds per task ID)
DELAY=$((SLURM_ARRAY_TASK_ID * 5))
echo "Delaying start by $DELAY seconds"
sleep $DELAY

module load openjdk

export PATH=$PATH:/scratch1/brendajm/tools/fragpipe/bin

# Define the base directory
BASE_DIR="/scratch1/brendajm/tmt_rosmap"

# Construct the specific directory for this array task
DIR="${BASE_DIR}/b${SLURM_ARRAY_TASK_ID}"

# Set the output file
OUTPUT_FILE="${DIR}/b${SLURM_ARRAY_TASK_ID}_tmt.out"

# Create annotation content dynamically based on SLURM_ARRAY_TASK_ID
ANNOTATION_CONTENT=$(cat << EOF
126     b${SLURM_ARRAY_TASK_ID}.126
127C    b${SLURM_ARRAY_TASK_ID}.127C
127N    b${SLURM_ARRAY_TASK_ID}.127N
128C    b${SLURM_ARRAY_TASK_ID}.128C
128N    b${SLURM_ARRAY_TASK_ID}.128N
129C    b${SLURM_ARRAY_TASK_ID}.129C
129N    b${SLURM_ARRAY_TASK_ID}.129N
130C    b${SLURM_ARRAY_TASK_ID}.130C
130N    b${SLURM_ARRAY_TASK_ID}.130N
131N    b${SLURM_ARRAY_TASK_ID}.131
EOF
)

# Delay the start of each job based on the SLURM_ARRAY_TASK_ID (e.g., 10 seconds per task ID)
DELAY=$((SLURM_ARRAY_TASK_ID * 5))
echo "Delaying start by $DELAY seconds"
sleep $DELAY

# Cap Java memory to 140GB
JAVA_MEM="150G"
export JAVA_OPTS="-Xmx${JAVA_MEM}"
echo "Capping Java memory to: ${JAVA_MEM}"

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

  # Check if the fragpipe_results directory exists, create it if it doesn't
  if [ ! -d "${DIR}/shortstop_proteogenomics_appended_results_cpm05" ]; then
    mkdir "${DIR}/shortstop_proteogenomics_appended_results_cpm05"
  fi

  # Check to make sure fragpipe_results directory is empty and delete everything in it if it's not
  if [ "$(ls -A "${DIR}/shortstop_proteogenomics_appended_results_cpm05")" ]; then
    rm -rf "${DIR}//shortstop_proteogenomics_appended_results_cpm05"/*
  fi

  cp "${BASE_DIR}/fragpipe_processing_files/tmt_shortstop_appended_rescored.workflow" "${DIR}"

  # Run fragpipe with the specified parameters
  fragpipe --headless \
    --workflow "${DIR}/tmt_shortstop_appended_rescored.workflow" \
    --manifest "${DIR}/b${SLURM_ARRAY_TASK_ID}.manifest" \
    --workdir "${DIR}/shortstop_proteogenomics_appended_results_cpm05" \
    --config-tools-folder /scratch1/brendajm/tools/ \
    --config-python /apps/spack/2406/apps/linux-rocky8-x86_64_v3/gcc-13.3.0/python-3.11.9-x74mtjf/bin/python
else
  echo "Directory $DIR does not exist." &> "$OUTPUT_FILE"
fi
