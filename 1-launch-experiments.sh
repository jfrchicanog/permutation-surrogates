#!/bin/bash
set -e
set -o pipefail

# Find our own location.
BINDIR=$(dirname "$(readlink -f "$(type -P $0 || echo $0)")")

slurm_job() {
	instance=$1
    JOBNAME=${instance}
    # FIXME: "sbatch <<EOF" should be enough
    # FC: it does not work
    cat <<EOF > kk.sh
#!/usr/bin/env bash
# The name to show in queue lists for this job:
#SBATCH -J $JOBNAME
#SBATCH --array=1-$nruns
# Number of desired cpus:
#SBATCH --cpus-per-task=1

# Amount of RAM needed for this job:
#SBATCH --mem=20gb

# The time the job will be running:
#SBATCH --time=20:00:00

# To use GPUs you have to request them:
##SBATCH --gres=gpu:1
#SBATCH --constraint=cal

# Set output and error files
#SBATCH --error=$OUTDIR/${JOBNAME}_%J.stderr
#SBATCH --output=$OUTDIR/${JOBNAME}_%J.stdout

# To load some software (you can show the list with 'module avail'):

echo "running: python3 fourier.py ${INSTANCE_DIR}/${instance} ${OUTDIR}/${instance}.out"
python3 fourier.py ${INSTANCE_DIR}/${instance} ${OUTDIR}/${instance}.out
EOF
sbatch kk.sh
rm kk.sh
}

nruns=1
LAUNCHER=slurm_job
mkdir -p ${BINDIR}/results
OUTDIR=${BINDIR}/results
INSTANCE_DIR=${BINDIR}/SMTWTP_small

$LAUNCHER n4.txt 

