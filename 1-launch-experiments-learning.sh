#!/bin/bash
set -e
set -o pipefail

# Find our own location.
BINDIR=$(dirname "$(readlink -f "$(type -P $0 || echo $0)")")

slurm_job() {
    problem=$1
    instance=$2
    trainingStart=$3
    trainingEnd=$4
    trainingIncrement=$5
    randomSeed=$5
    order=$6
    irreps=$7
    JOBNAME=${problem}-${instance}-seed${randomSeed}-${order}
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
#SBATCH --time=20:00:00

# To use GPUs you have to request them:
##SBATCH --gres=gpu:1
#SBATCH --constraint=cal

# Set output and error files
#SBATCH --error=$OUTDIR/${JOBNAME}_%J.stderr
#SBATCH --output=$OUTDIR/${JOBNAME}_%J.stdout

# To load some software (you can show the list with 'module avail'):

COMMAND="python3 learning-surrogate.py --problem $problem --instance ${INSTANCE_DIR}/${instance} --trainingStart ${trainingStart} --trainingEnd ${trainingEnd} --trainingIncrement ${trainingIncrement} --randomSeed ${randomSeed} --irreps $irreps --output ${OUTDIR}/${JOBNAME}.out"
echo \$COMMAND
\$COMMAND
EOF
sbatch kk.sh
rm kk.sh
}

#nruns=1
#LAUNCHER=slurm_job
#mkdir -p ${BINDIR}/results
#OUTDIR=${BINDIR}/results
#INSTANCE_DIR=${BINDIR}/SMTWTP_small

#for instance in `cat smwtp-instances-to-solve.txt`; do
#	$LAUNCHER smwtp $instance
#done


nruns=1
LAUNCHER=slurm_job
OUTDIR="${BINDIR}/results/arp/learning"
INSTANCE_DIR="${BINDIR}/arp"
mkdir -p "${OUTDIR}"

irreps5=('[5]' '[5],[4,1]' '[5],[4,1],[3,2],[3,1,1]' '[5],[4,1],[3,2],[3,1,1],[2,2,1],[2,1,1,1]' '[5],[4,1],[3,2],[3,1,1],[2,2,1],[2,1,1,1],[1,1,1,1,1]')
irreps6=('[6]' '[6],[5,1]' '[6],[5,1],[4,2],[4,1,1]' '[6],[5,1],[4,2],[4,1,1],[3,3],[3,2,1],[3,1,1,1]' '[6],[5,1],[4,2],[4,1,1],[3,3],[3,2,1],[3,1,1,1],[2,2,2],[2,2,1,1],[2,1,1,1,1]')
irreps7=('[7]' '[7],[6,1]' '[7],[6,1],[5,2],[5,1,1]' '[7],[6,1],[5,2],[5,1,1],[4,3],[4,2,1],[4,1,1,1]' '[7],[6,1],[5,2],[5,1,1],[4,3],[4,2,1],[4,1,1,1],[3,3,1],[3,2,2],[3,2,1,1],[3,1,1,1,1]')
irreps8=('[8]' '[8],[7,1]' '[8],[7,1],[6,2],[6,1,1]' '[8],[7,1],[6,2],[6,1,1],[5,3],[5,2,1],[5,1,1,1]' '[8],[7,1],[6,2],[6,1,1],[5,3],[5,2,1],[5,1,1,1],[4,4],[4,3,1],[4,2,2],[4,2,1,1],[4,1,1,1,1]')
irreps9=('[9]' '[9],[8,1]' '[9],[8,1],[7,2],[7,1,1]' '[9],[8,1],[7,2],[7,1,1],[6,3],[6,2,1],[6,1,1,1]' '[9],[8,1],[7,2],[7,1,1],[6,3],[6,2,1],[6,1,1,1],[5,4],[5,3,1],[5,2,2],[5,2,1,1],[5,1,1,1,1]')
irreps10=('[10]' '[10],[9,1]' '[10],[9,1],[8,2],[8,1,1]' '[10],[9,1],[8,2],[8,1,1],[7,3],[7,2,1],[7,1,1,1]' '[10],[9,1],[8,2],[8,1,1],[7,3],[7,2,1],[7,1,1,1],[6,4],[6,3,1],[6,2,2],[6,2,1,1],[6,1,1,1,1]')


training5=(5 120 5)
training6=(10 720 10)
training7=(15 1080 15)
training8=(20 400 20)
training9=(20 400 20)
training10=(20 400 20)

order=(0 1 2 3 4)

# Size 5
for instance in $(find -L arp -name arp_5_\* -printf %f\\n); do 
    for ((i=0;i<${#irreps5[@]}-1;i++)); do
        irrep=${irreps5[i]}
        for seed in $(seq 1 10); do
            $LAUNCHER samples $instance ${training5[0]} ${training5[1]} ${training5[2]} $seed ${order[i]} $irrep
        done 
    done
done


