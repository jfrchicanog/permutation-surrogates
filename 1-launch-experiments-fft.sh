#!/bin/bash
set -e
set -o pipefail

# Find our own location.
BINDIR=$(dirname "$(readlink -f "$(type -P $0 || echo $0)")")

slurm_job() {
    problem=$1
    instance=$2
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
#SBATCH --mem=2gb

# The time the job will be running:
#SBATCH --time=1-00:00:00

# To use GPUs you have to request them:
##SBATCH --gres=gpu:1
#SBATCH --constraint=cal

# Set output and error files
#SBATCH --error=$OUTDIR/${JOBNAME}_%J.stderr
#SBATCH --output=$OUTDIR/${JOBNAME}_%J.stdout

# To load some software (you can show the list with 'module avail'):

COMMAND="python3 fft.py --problem $problem --instance ${INSTANCE_DIR}/${instance} --output ${OUTDIR}/${instance}.fft"
echo \$COMMAND
\$COMMAND
EOF
sbatch kk.sh
rm kk.sh
}

#nruns=1
#LAUNCHER=slurm_job
#mkdir -p ${BINDIR}/results/smtwtp
#OUTDIR=${BINDIR}/results/smtwtp
#INSTANCE_DIR=${BINDIR}/smtwtp

#for instance in `cat smwtp-instances-to-solve.txt`; do
#	$LAUNCHER smwtp $instance
#done


nruns=1
LAUNCHER=slurm_job
OUTDIR="${BINDIR}/results/arp"
INSTANCE_DIR="${BINDIR}/arp"
mkdir -p "${OUTDIR}"

for instance in `cat arp-instances-to-solve.txt`; do
	$LAUNCHER samples $instance
done
