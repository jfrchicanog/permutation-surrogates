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
    JOBNAME=${problem}-${instance}-${trainingStart}-${trainingEnd}-${trainingIncrement}
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
#SBATCH --mem=5gb

# The time the job will be running:
#SBATCH --time=20:00:00

# To use GPUs you have to request them:
##SBATCH --gres=gpu:1
#SBATCH --constraint=cal

# Set output and error files
#SBATCH --error=$OUTDIR/${JOBNAME}_%J.stderr
#SBATCH --output=$OUTDIR/${JOBNAME}_%J.stdout

# To load some software (you can show the list with 'module avail'):
run=\$SLURM_ARRAY_TASK_ID
randomSeed=\$run

irreps=(${irreps[@]})
orders=(${orders[@]})

for ((i=0;i<\${#orders[@]};i++)); do
    COMMAND="python3 learning-surrogate.py --problem $problem --instance ${INSTANCE_DIR}/${instance} --trainingStart ${trainingStart} --trainingEnd ${trainingEnd} --trainingIncrement ${trainingIncrement} --randomSeed \${randomSeed} --irreps \${irreps[i]} --output ${OUTDIR}/${JOBNAME}-order\${orders[i]}-seed\${randomSeed}-f${date}.out"
    echo "running: " \$COMMAND
    \$COMMAND
done

EOF
sbatch kk.sh
rm kk.sh
}

configureSize() {
    size=$1

    if [ "$size" == 5 ];
        irreps=('[5]' '[5],[4,1]' '[5],[4,1],[3,2],[3,1,1]' '[5],[4,1],[3,2],[3,1,1],[2,2,1],[2,1,1,1]' '[5],[4,1],[3,2],[3,1,1],[2,2,1],[2,1,1,1],[1,1,1,1,1]')
        order=(0 1 2 3 4)
        training=(2 200 2)
    elif [ "$size" == 6 ];
        irreps=('[6]' '[6],[5,1]' '[6],[5,1],[4,2],[4,1,1]' '[6],[5,1],[4,2],[4,1,1],[3,3],[3,2,1],[3,1,1,1]' '[6],[5,1],[4,2],[4,1,1],[3,3],[3,2,1],[3,1,1,1],[2,2,2],[2,2,1,1],[2,1,1,1,1]')
        order=(0 1 2 3 4)
        training=(14 1400 14)
    elif [ "$size" == 7 ];
        irreps=('[7]' '[7],[6,1]' '[7],[6,1],[5,2],[5,1,1]' '[7],[6,1],[5,2],[5,1,1],[4,3],[4,2,1],[4,1,1,1]' '[7],[6,1],[5,2],[5,1,1],[4,3],[4,2,1],[4,1,1,1],[3,3,1],[3,2,2],[3,2,1,1],[3,1,1,1,1]')
        order=(0 1 2 3 4)
        training=(90 9000 90)
    elif [ "$size" == 8 ];
        irreps=('[8]' '[8],[7,1]' '[8],[7,1],[6,2],[6,1,1]' '[8],[7,1],[6,2],[6,1,1],[5,3],[5,2,1],[5,1,1,1]' '[8],[7,1],[6,2],[6,1,1],[5,3],[5,2,1],[5,1,1,1],[4,4],[4,3,1],[4,2,2],[4,2,1,1],[4,1,1,1,1]')
        order=(0 1 2)
        training=(18 1800 18)
    elif [ "$size" == 9 ];
        irreps=('[9]' '[9],[8,1]' '[9],[8,1],[7,2],[7,1,1]' '[9],[8,1],[7,2],[7,1,1],[6,3],[6,2,1],[6,1,1,1]' '[9],[8,1],[7,2],[7,1,1],[6,3],[6,2,1],[6,1,1,1],[5,4],[5,3,1],[5,2,2],[5,2,1,1],[5,1,1,1,1]')
        order=(0 1 2)
        training=(32 3200 32)
    elif [ "$size" == 10 ];
        irreps=('[10]' '[10],[9,1]' '[10],[9,1],[8,2],[8,1,1]' '[10],[9,1],[8,2],[8,1,1],[7,3],[7,2,1],[7,1,1,1]' '[10],[9,1],[8,2],[8,1,1],[7,3],[7,2,1],[7,1,1,1],[6,4],[6,3,1],[6,2,2],[6,2,1,1],[6,1,1,1,1]')
        order=(0 1 2)
        training=(52 5200 52)
    else
        echo "Invalid size ${size}"
        exit

}

launchARP() {
    size=$1
    configureSize $size

    INSTANCE_DIR="${BINDIR}/arp"
    OUTDIR="${BINDIR}/results/arp/learning/n${size}"
    mkdir -p "${OUTDIR}"

    for instance in $(find -L ${INSTANCE_DIR} -name arp_${size}_\* -printf %f\\n); do 
        $LAUNCHER samples $instance ${training[0]} ${training[1]} ${training[2]}
    done

}

launchSMWTP() {
    size=$1
    configureSize $size

    INSTANCE_DIR="${BINDIR}/SMTWTP_small"
    OUTDIR="${BINDIR}/results/smwtp/learning/n${size}"
    mkdir -p "${OUTDIR}"

    for instance in $(find -L ${INSTANCE_DIR} -name n${size}_\* -printf %f\\n); do 
        $LAUNCHER smwtp $instance ${training[0]} ${training[1]} ${training[2]}
    done

}

problem=$1
size=$2
date=$(date +%d%m%Y-%H%M%S)
nruns=10
LAUNCHER=slurm_job

if [ "$problem" == 'smwtp' ];
    launchMWTP $size
elif [ "$problem" == 'arp' ];
    launchARP $size
else
    echo "Unknown problem ${problem}"
fi

